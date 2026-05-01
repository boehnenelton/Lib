
import os
import sys
import shutil
import unittest
import zipfile
from pathlib import Path

# Add lib paths
sys.path.append('/storage/emulated/0/dev/lib/py')

import lib_mfdb_core as mfdb
import lib_mfdb_validator as validator

class TestMFDBArchiveV12(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = Path("/storage/emulated/0/dev/lib/tests/py/temp_db")
        cls.mount_dir = Path("/storage/emulated/0/dev/lib/tests/py/mount_point")
        cls.archive_path = Path("/storage/emulated/0/dev/lib/tests/py/test_db.mfdb.zip")
        
        if cls.test_dir.exists(): shutil.rmtree(cls.test_dir)
        if cls.mount_dir.exists(): shutil.rmtree(cls.mount_dir)
        if cls.archive_path.exists(): os.remove(cls.archive_path)

        # Create a dummy MFDB
        entities = [
            {"name": "TestEntity", "fields": [{"name": "id", "type": "integer"}, {"name": "data", "type": "string"}]}
        ]
        mfdb.mfdb_core_create_database(str(cls.test_dir), "TestDB", entities)
        
        # Package it manually for the first mount test
        with zipfile.ZipFile(cls.archive_path, 'w') as zipf:
            for root, dirs, files in os.walk(cls.test_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), cls.test_dir))

    def test_01_discovery(self):
        role = mfdb.mfdb_core_discover(str(self.archive_path))
        self.assertEqual(role, "archive")

    def test_02_mount(self):
        manifest_path = mfdb.MFDBArchive.mount(str(self.archive_path), str(self.mount_dir))
        self.assertTrue(os.path.exists(manifest_path))
        self.assertTrue((self.mount_dir / ".mfdb_lock").exists())

    def test_03_data_integrity(self):
        # Should be able to load entity from mount point
        manifest_path = str(self.mount_dir / "104a.mfdb.bejson")
        records = mfdb.mfdb_core_load_entity(manifest_path, "TestEntity")
        self.assertEqual(len(records), 0)

    def test_04_atomic_commit(self):
        manifest_path = str(self.mount_dir / "104a.mfdb.bejson")
        mfdb.mfdb_core_add_entity_record(manifest_path, "TestEntity", [1, "Hello World"])
        
        # Commit back to archive
        mfdb.MFDBArchive.commit(str(self.mount_dir))
        
        # Verify the zip contains the change without extracting
        with zipfile.ZipFile(self.archive_path, 'r') as zipf:
            with zipf.open('data/testentity.bejson') as f:
                data = f.read().decode('utf-8')
                self.assertIn("Hello World", data)

    def test_05_conflict(self):
        # Attempt to mount already locked dir from same process should work with force or fail without
        with self.assertRaises(mfdb.MFDBCoreError):
            # Simulate a different PID lock
            lock_file = self.mount_dir / ".mfdb_lock"
            import json
            with open(lock_file, 'w') as f:
                json.dump({"pid": 99999, "mounted_at": "now"}, f)
            
            mfdb.MFDBArchive.mount(str(self.archive_path), str(self.mount_dir))

    def test_06_validation(self):
        self.assertTrue(validator.mfdb_validator_validate_archive(str(self.archive_path)))
        
        # Create invalid archive
        bad_arc = Path("/storage/emulated/0/dev/lib/tests/py/bad.mfdb.zip")
        with zipfile.ZipFile(bad_arc, 'w') as zipf:
            zipf.writestr("nothing.txt", "hello")
        
        with self.assertRaises(validator.MFDBValidationError):
            validator.mfdb_validator_validate_archive(str(bad_arc))

    @classmethod
    def tearDownClass(cls):
        if cls.test_dir.exists(): shutil.rmtree(cls.test_dir)
        # Keep mount_dir and archive for report inspection if needed, but usually cleanup
        # shutil.rmtree(cls.mount_dir)
        # os.remove(cls.archive_path)

if __name__ == '__main__':
    unittest.main()
