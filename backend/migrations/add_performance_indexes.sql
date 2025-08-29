-- Performance optimization indexes for Data Intelligence Platform
-- Generated for code quality improvements

-- Index on uploaded_files for frequent session-based queries
CREATE INDEX IF NOT EXISTS idx_uploaded_files_session_id ON uploaded_files(session_id);

-- Index on uploaded_files for file retrieval by user and session
CREATE INDEX IF NOT EXISTS idx_uploaded_files_user_session ON uploaded_files(user_id, session_id);

-- Index on uploaded_files for file name searches
CREATE INDEX IF NOT EXISTS idx_uploaded_files_filename ON uploaded_files(filename);

-- Composite index for file queries with timestamp ordering
CREATE INDEX IF NOT EXISTS idx_uploaded_files_created_at ON uploaded_files(created_at DESC);

-- Index for session management queries
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(is_active) WHERE is_active = true;

-- Index for query history and analytics
CREATE INDEX IF NOT EXISTS idx_query_history_session ON query_history(session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_query_history_user ON query_history(user_id, created_at DESC);

-- Index for file processing jobs
CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_file_id ON processing_jobs(file_id);

-- Index for statistics and analytics
CREATE INDEX IF NOT EXISTS idx_statistics_file_session ON statistics(file_id, session_id);

-- Full-text search index for query content (if using PostgreSQL)
-- CREATE INDEX IF NOT EXISTS idx_query_content_fts ON query_history USING gin(to_tsvector('english', query_text));

-- Performance monitoring indexes
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_operation ON performance_metrics(operation_type, timestamp DESC);

COMMENT ON INDEX idx_uploaded_files_session_id IS 'Optimize file retrieval by session';
COMMENT ON INDEX idx_uploaded_files_user_session IS 'Optimize user-specific file queries';
COMMENT ON INDEX idx_sessions_expires_at IS 'Optimize session cleanup operations';
COMMENT ON INDEX idx_query_history_session IS 'Optimize chat history retrieval';