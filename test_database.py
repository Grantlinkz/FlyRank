import os
import unittest
from concurrent.futures import ThreadPoolExecutor

os.environ["DATABASE_URL"] = "sqlite:///test_tasks.db"
import database

class TestDatabaseConcurrency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.DATABASE_URL = "sqlite:///test_tasks.db"
        database.init_db()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists("test_tasks.db"):
            try:
                os.remove("test_tasks.db")
            except Exception:
                pass

    def test_concurrent_independent_updates(self):
        """Verify that concurrent updates to title and done do not overwrite each other."""
        # Create an initial task
        task = database.create_task("Original Title")
        task_id = task["id"]
        self.assertFalse(task["done"])

        # Define independent update callables
        def update_title():
            return database.update_task(task_id, title="Concurrent Updated Title")

        def update_done():
            return database.update_task(task_id, done=True)

        # Run both updates concurrently using thread pool executor
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_title = executor.submit(update_title)
            future_done = executor.submit(update_done)
            res_title = future_title.result()
            res_done = future_done.result()

        # Fetch final state from database
        final_task = database.get_task_by_id(task_id)
        
        # Both independent updates must be preserved in final state
        self.assertEqual(final_task["title"], "Concurrent Updated Title")
        self.assertTrue(final_task["done"])

        # Clean up created task
        database.delete_task(task_id)

if __name__ == "__main__":
    unittest.main()
