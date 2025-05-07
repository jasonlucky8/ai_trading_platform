import unittest
import redis
from src.data.redis_storage import RedisStorage 
from src.data.storage_factory import StorageFactory

class TestRedisStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        cls.redis_client.flushdb()
        
    def setUp(self):
        self.storage = StorageFactory.create_storage('redis')
        
    def test_store_and_retrieve(self):
        test_data = {'symbol': 'BTC/USDT', 'price': 50000.0}
        self.storage.store('test_key', test_data)
        retrieved = self.storage.retrieve('test_key')
        self.assertEqual(retrieved, test_data)
        
    def test_retrieve_nonexistent(self):
        result = self.storage.retrieve('nonexistent_key')
        self.assertIsNone(result)
        
    def test_store_update(self):
        initial_data = {'symbol': 'ETH/USDT', 'price': 3000.0}
        updated_data = {'symbol': 'ETH/USDT', 'price': 3100.0}
        
        self.storage.store('update_key', initial_data)
        self.storage.store('update_key', updated_data)
        
        retrieved = self.storage.retrieve('update_key')
        self.assertEqual(retrieved, updated_data)

if __name__ == '__main__':
    unittest.main()
