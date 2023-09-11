/* global use, db */
// MongoDB Playground
// Use Ctrl+Space inside a snippet or a string literal to trigger completions.

// The current database to use.
use("blogdb");

// Search for documents in the current collection.
db.getCollection("animes").aggregate([
  {
    $search: {
      index: "animes",
      text: {
        query: "shakugan no shana",
        path: {
          wildcard: "*",
        },
      },
    },
  },
]);
