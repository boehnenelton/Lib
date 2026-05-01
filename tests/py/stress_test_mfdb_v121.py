
import os
import sys
import shutil
import unittest
import time
import random
from pathlib import Path

# Add lib paths
sys.path.append('/storage/emulated/0/dev/lib/py')

import lib_mfdb_core as mfdb
import lib_mfdb_validator as validator
from lib_mfdb_validator import MFDBValidationError
from lib_bejson_core import BEJSONCoreError

class StressTestMFDBv121(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path("/storage/emulated/0/dev/lib/tests/py/stress_test_root")
        cls.mount_dir = Path("/storage/emulated/0/dev/lib/tests/py/stress_mount")
        cls.archive_path = Path("/storage/emulated/0/dev/lib/tests/py/stress_db.mfdb.zip")
        
        if cls.root_dir.exists(): shutil.rmtree(cls.root_dir)
        if cls.mount_dir.exists(): shutil.rmtree(cls.mount_dir)
        if cls.archive_path.exists(): os.remove(cls.archive_path)
        cls.root_dir.mkdir(parents=True, exist_ok=True)

    def test_01_heavy_initialization(self):
        """Create a multi-entity database with many records."""
        print("\n[STRESS] Phase 1: Heavy Initialization")
        entities = [
            {"name": "Users", "fields": [{"name": "uid", "type": "integer"}, {"name": "username", "type": "string"}], "primary_key": "uid"},
            {"name": "Posts", "fields": [{"name": "pid", "type": "integer"}, {"name": "uid_fk", "type": "integer"}, {"name": "content", "type": "string"}], "primary_key": "pid"},
            {"name": "Logs", "fields": [{"name": "lid", "type": "integer"}, {"name": "msg", "type": "string"}]}
        ]
        
        manifest_path = mfdb.mfdb_core_create_database(str(self.root_dir), "StressDB", entities)
        self.assertTrue(os.path.exists(manifest_path))
        
        # Add 100 users
        for i in range(100):
            mfdb.mfdb_core_add_entity_record(manifest_path, "Users", [i, f"user_{i}"])
        
        # Add 500 posts
        for i in range(500):
            uid = i % 100
            mfdb.mfdb_core_add_entity_record(manifest_path, "Posts", [i, uid, f"Post content for {i}"])
            
        # Verify counts
        stats = mfdb.mfdb_core_get_stats(manifest_path)
        self.assertEqual(stats["entities"][0]["record_count"], 100)
        self.assertEqual(stats["entities"][1]["record_count"], 500)
        print(f"[STRESS] Initialized {stats['entity_count']} entities with total {100+500} records.")

    def test_02_archive_and_mount(self):
        """Package the heavy DB and mount it."""
        print("\n[STRESS] Phase 2: Archive and Mount")
        # Manually package initially (or we could use a helper if we had one for zipping an existing dir)
        import zipfile
        with zipfile.ZipFile(self.archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.root_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), self.root_dir))
        
        manifest_path = mfdb.MFDBArchive.mount(str(self.archive_path), str(self.mount_dir))
        self.assertTrue(os.path.exists(manifest_path))
        print(f"[STRESS] Mounted archive to {self.mount_dir}")

    def test_03_recovery_missing_entity(self):
        """Delete an entity file and test smart repair."""
        print("\n[STRESS] Phase 3: Missing Entity Recovery (Error 33)")
        manifest_path = str(self.mount_dir / "104a.mfdb.bejson")
        posts_path = self.mount_dir / "data" / "posts.bejson"
        
        # 1. Break it: Delete posts entity
        self.assertTrue(posts_path.exists())
        os.remove(posts_path)
        self.assertFalse(posts_path.exists())
        
        # 2. Validate it: Expect Error 33
        with self.assertRaises(MFDBValidationError) as cm:
            validator.mfdb_validator_validate_database(manifest_path)
        self.assertEqual(cm.exception.code, 33)
        print(f"[STRESS] Caught expected Error 33: {cm.exception}")
        
        # 3. Repair it
        success = mfdb.mfdb_core_smart_repair(manifest_path, cm.exception)
        self.assertTrue(success)
        self.assertTrue(posts_path.exists())
        print("[STRESS] Smart repair successfully resurrected posts.bejson")
        
        # 4. Final verify
        self.assertTrue(validator.mfdb_validator_validate_database(manifest_path))

    def test_04_recovery_broken_hierarchy(self):
        """Break Parent_Hierarchy and test smart repair."""
        print("\n[STRESS] Phase 4: Broken Hierarchy Recovery (Error 38)")
        manifest_path = str(self.mount_dir / "104a.mfdb.bejson")
        users_path = self.mount_dir / "data" / "users.bejson"
        
        # 1. Break it: Point to a non-existent manifest
        from lib_bejson_core import bejson_core_load_file, bejson_core_atomic_write
        doc = bejson_core_load_file(str(users_path))
        doc["Parent_Hierarchy"] = "../../wrong/path.bejson"
        bejson_core_atomic_write(str(users_path), doc)
        
        # 2. Validate it: Expect Error 37 or 38
        with self.assertRaises(MFDBValidationError) as cm:
            validator.mfdb_validator_validate_database(manifest_path)
        self.assertIn(cm.exception.code, (37, 38))
        print(f"[STRESS] Caught expected Error {cm.exception.code}: {cm.exception}")
        
        # 3. Repair it
        success = mfdb.mfdb_core_smart_repair(manifest_path, cm.exception)
        self.assertTrue(success)
        
        # 4. Verify repair fixed the header
        new_doc = bejson_core_load_file(str(users_path))
        self.assertEqual(new_doc["Parent_Hierarchy"], "../104a.mfdb.bejson")
        print("[STRESS] Smart repair successfully patched Parent_Hierarchy")
        
        # 5. Final verify
        self.assertTrue(validator.mfdb_validator_validate_database(manifest_path))

    def test_05_heavy_mutation_and_commit(self):
        """Add more records and commit everything back."""
        print("\n[STRESS] Phase 5: Heavy Mutation and Commit")
        manifest_path = str(self.mount_dir / "104a.mfdb.bejson")
        
        # Add 400 more posts (bringing total to 900)
        for i in range(500, 900):
            mfdb.mfdb_core_add_entity_record(manifest_path, "Posts", [i, i % 100, f"New post {i}"])
            
        print("[STRESS] Added 400 more records in mounted workspace.")
        
        # Commit
        new_archive = mfdb.MFDBArchive.commit(str(self.mount_dir))
        self.assertEqual(new_archive, str(self.archive_path))
        
        # Re-mount to verify
        shutil.rmtree(self.mount_dir)
        manifest_path = mfdb.MFDBArchive.mount(str(self.archive_path), str(self.mount_dir))
        stats = mfdb.mfdb_core_get_stats(manifest_path)
        self.assertEqual(stats["entities"][1]["record_count"], 900)
        print(f"[STRESS] Final verification: Posts count = {stats['entities'][1]['record_count']} (Expected 900)")

    @classmethod
    def tearDownClass(cls):
        # Clean up
        if cls.root_dir.exists(): shutil.rmtree(cls.root_dir)
        if cls.mount_dir.exists(): shutil.rmtree(cls.mount_dir)
        if cls.archive_path.exists(): os.remove(cls.archive_path)

if __name__ == '__main__':
    unittest.main()
