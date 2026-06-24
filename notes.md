CodeVector Take Home Submission Notes

Ayan

Things I Chose and Why

FastAPI - I chose FastAPI because I am most comfortable with Python and it provides automatic validation good performance and a clean structure for building APIs quickly It also keeps the code easy to understand and explain during the interview

PostgreSQL - I chose PostgreSQL because it handles large datasets efficiently and supports the indexing and query patterns needed for fast pagination and filtering

NeonDB - I chose Neon because it provides a free PostgreSQL database is easy to set up

SQLAlchemy - I chose SQLAlchemy because it provides a clean way to interact with PostgreSQL while still allowing me to write optimized queries when needed

Cursor Based Pagination - I chose cursor pagination instead of offset pagination because offset queries become slower as the page number increases and can produce duplicates or skipped products when new data is inserted while users are browsing

Session Snapshot - I added a session timestamp to every browsing session so users see a consistent view of the dataset while paginating This prevents newly inserted products from affecting the pages they are currently browsing

Composite Cursor- created at id I used both created at and id in the cursor because multiple products can share the same timestamp Using both values guarantees a stable and unique ordering

Database Indexes- I created indexes for pagination category filtering and new product detection so PostgreSQL can use index scans instead of scanning all 200000 rows for every request

Bulk Data Generation - I used PostgreSQL COPY for seeding because inserting 200000 rows individually is slow Bulk loading is significantly faster and more suitable for generating large datasets

What I Would Improve With More Time

Redis Caching - I would cache expensive counts and frequently accessed data to reduce database load as the dataset grows

WebSockets or SSE- I would replace polling with real time updates so users are notified instantly when new products are added

Full Text Search - I would add PostgreSQL full text search so users can search across all products efficiently

Testing - I would add unit and integration tests especially around pagination edge cases where products are inserted while users are browsing

Production Readiness- I would add rate limiting structured logging monitoring error tracking and more detailed deployment configuration

How I Used AI

Claude - I used Claude to discuss different pagination approaches understand PostgreSQL tuple comparisons generate boilerplate code and speed up implementation I reviewed all generated code and made changes where necessaryting

Overall AI helped reduce development time and generate boilerplate but I made the final architecture decisions verified the approach and ensured it met the requirements of the assignment and also the documentation
