import { openDB } from 'idb';

const DB_NAME = 'LostnFound_Drafts';
const STORE_NAME = 'drafts';
const DB_VERSION = 1;

const dbPromise = openDB(DB_NAME, DB_VERSION, {
  upgrade(db) {
    if (!db.objectStoreNames.contains(STORE_NAME)) {
      db.createObjectStore(STORE_NAME);
    }
  },
});

export const DraftService = {
  async saveDraft(key, data) {
    const db = await dbPromise;
    return db.put(STORE_NAME, data, key);
  },

  async getDraft(key) {
    const db = await dbPromise;
    return db.get(STORE_NAME, key);
  },

  async deleteDraft(key) {
    const db = await dbPromise;
    return db.delete(STORE_NAME, key);
  },

  async clearAll() {
    const db = await dbPromise;
    return db.clear(STORE_NAME);
  }
};
