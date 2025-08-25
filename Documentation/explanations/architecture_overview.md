# System Architecture Overview

## Introduction

The Equity Valuation System is designed as a modern, microservices-inspired application that separates concerns between data ingestion, transformation, and presentation. This architectural overview explains the design decisions, component interactions, and scalability considerations that shape the system's structure.

## Architectural Principles

### Design Philosophy

The system is built on several key architectural principles:

**Modularity**: Each major functional area (authentication, data providers, transformation, valuation) is implemented as a separate module with clear interfaces and minimal coupling.

**Extensibility**: The pluggable data provider architecture allows new financial data sources to be integrated without modifying core system logic.

**Security by Design**: Authentication, authorization, and data protection are built into the foundation rather than added as an afterthought.

**Data Integrity**: Comprehensive data validation, transformation tracking, and audit trails ensure the reliability of financial calculations.

**Performance**: Strategic caching, database indexing, and efficient data structures support real-time analysis of large financial datasets.

## High-Level Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   React/TS      │◄──►│   FastAPI       │◄──►│   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Data Providers  │
                       │ Kaggle, Yahoo,  │
                       │ Alpha Vantage   │
                       └─────────────────┘
```

### Component Responsibilities

**Frontend (React/TypeScript)**
- User interface and experience
- Real-time data visualization
- Client-side routing and state management
- Authentication token management

**Backend API (FastAPI)**
- REST API endpoints
- Business logic orchestration
- Authentication and authorization
- Data transformation coordination

**Database (PostgreSQL)**
- Persistent data storage
- ACID transaction support
- Complex query optimization
- Data integrity constraints

**Data Providers**
- External data source integration
- Rate limiting and connection management
- Data format normalization
- Error handling and retry logic

## Detailed Component Architecture

### Frontend Architecture

The frontend follows a modern React architecture with functional components and hooks:

```
src/
├── components/          # Reusable UI components
│   ├── Layout/         # Application layout and navigation
│   ├── ProtectedRoute/ # Authentication guards
│   ├── PriceChart/     # Financial data visualization
│   └── ThemeToggle/    # UI theme management
├── pages/              # Route-level components
│   ├── Dashboard/      # Main application dashboard
│   ├── Companies/      # Company management
│   ├── Valuations/     # Valuation results
│   └── Providers/      # Data provider configuration
├── contexts/           # Global state management
│   ├── AuthContext/    # User authentication state
│   └── ThemeContext/   # UI theme state
└── services/           # API client services
    ├── auth.ts         # Authentication API calls
    ├── companies.ts    # Company data API calls
    └── providers.ts    # Data provider API calls
```

**State Management Strategy**
- **React Context**: Global state for authentication and theming
- **Local State**: Component-level state using React hooks
- **Server State**: API data managed through custom hooks
- **Form State**: Controlled components with validation

### Backend Architecture

The backend implements a layered architecture with clear separation of concerns:

```
backend/
├── main.py             # FastAPI application entry point
├── auth/               # Authentication and authorization
│   ├── models.py       # User and session models
│   ├── routes.py       # Authentication endpoints
│   └── utils.py        # JWT and password utilities
├── db/                 # Database layer
│   ├── models/         # SQLAlchemy ORM models
│   ├── base.py         # Database connection setup
│   ├── session.py      # Session management
│   └── init_data.py    # Database initialization
├── data_providers/     # External data integration
│   ├── base_provider.py     # Abstract provider interface
│   ├── kaggle_provider.py   # Kaggle dataset integration
│   └── provider_factory.py  # Provider instantiation
├── services/           # Business logic layer
│   ├── transform_engine.py      # Data transformation
│   ├── formula_evaluator.py    # Financial calculations
│   └── financial_data_service.py # Data orchestration
├── routes/             # API endpoints
│   ├── valuation.py    # Valuation CRUD operations
│   ├── companies.py    # Company data management
│   ├── providers.py    # Data provider management
│   └── transform.py    # Data transformation endpoints
└── schemas/            # Pydantic data validation
    ├── valuation.py    # Valuation data schemas
    ├── provider.py     # Provider configuration schemas
    └── mapping.py      # Field mapping schemas
```

**Architectural Layers**
1. **Presentation Layer** (routes/): HTTP request/response handling
2. **Service Layer** (services/): Business logic and orchestration
3. **Data Access Layer** (db/models/): Database abstraction
4. **Integration Layer** (data_providers/): External system interfaces

### Database Architecture

The database design emphasizes data integrity, performance, and extensibility:

**Core Design Patterns**
- **UUID Primary Keys**: Enable distributed scaling and data migration
- **JSONB Storage**: Flexible storage for varying financial data formats
- **Composite Indexes**: Optimized for common query patterns
- **Foreign Key Constraints**: Maintain referential integrity
- **Audit Trails**: Track changes for compliance and debugging

**Performance Optimizations**
- **Strategic Indexing**: Indexes on common query patterns (company+date, provider+date)
- **Partitioning Strategy**: Future partitioning of large tables by date ranges
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Analyzed and optimized frequent queries

## Data Flow Architecture

### Data Ingestion Pipeline

The system implements a comprehensive data pipeline from raw external data to standardized financial metrics:

```
External APIs → Raw Data Storage → Field Mapping → Transformation → Canonical Storage
     │                │                  │              │               │
     │                │                  │              │               │
  Provider         raw_data_         mapped_fields   Transform      Canonical
 Connector          entries           Configuration   Engine         Fields
```

**Pipeline Stages**

1. **Data Acquisition**
   - Provider-specific API calls or file processing
   - Rate limiting and connection management
   - Error handling and retry mechanisms
   - Data quality validation

2. **Raw Data Storage**
   - Preserve original data format and values
   - Batch tracking for data lineage
   - Metadata capture (source, timestamp, quality)
   - Duplicate detection and handling

3. **Field Mapping Configuration**
   - Map provider fields to canonical field definitions
   - Support for company-specific mappings
   - Temporal validity (start/end dates)
   - Complex transformation rules

4. **Data Transformation**
   - Execute mathematical transformations
   - Unit conversions and standardization
   - Data validation against business rules
   - Error handling and partial success management

5. **Canonical Storage**
   - Standardized data format
   - Optimized for query performance
   - Comprehensive indexing
   - Data integrity constraints

### Authentication Flow

The system implements JWT-based authentication with comprehensive security measures:

```
Login Request → Credential Validation → JWT Generation → Token Storage → API Access
      │               │                      │              │             │
      │               │                      │              │             │
   Username/        Password               JWT Token      Browser       Protected
   Password         Hashing              with Claims     Storage       Endpoints
```

**Security Implementation**
- **Password Hashing**: Bcrypt with salt for secure password storage
- **JWT Tokens**: Short-lived access tokens with refresh capability
- **Token Validation**: Middleware validates tokens on protected routes
- **Role-Based Access**: User roles control access to specific features
- **Session Management**: Secure token storage and automatic expiration

## Integration Patterns

### Data Provider Integration

The system uses the Strategy pattern to enable pluggable data providers:

```python
# Abstract provider interface
class BaseDataProvider(ABC):
    @abstractmethod
    def test_connection(self) -> bool: pass
    
    @abstractmethod
    def get_available_tickers(self) -> Set[str]: pass
    
    @abstractmethod
    def ingest_historical_data(self, tickers, start_date, end_date) -> IngestionResult: pass
```

**Provider Implementation Benefits**
- **Extensibility**: Add new providers without modifying core logic
- **Testability**: Mock providers for unit testing
- **Consistency**: Uniform interface across all data sources
- **Configuration**: Runtime provider selection and configuration

### Transformation Engine Integration

The transformation engine provides secure, sandboxed mathematical calculations:

```python
# JSON-based expression evaluation
expression = {
    "op": "divide",
    "args": [
        {"field": "total_debt"},
        {"field": "total_equity"}
    ]
}

result = transform_engine.evaluate_expression(expression, financial_data)
```

**Security Considerations**
- **No Code Execution**: Only predefined mathematical operations allowed
- **Input Validation**: Strict validation of expression structure
- **Sandboxed Environment**: Isolated execution prevents system compromise
- **Error Boundaries**: Controlled error handling prevents system failure

## Scalability Considerations

### Horizontal Scaling Strategies

**Database Scaling**
- **Read Replicas**: Distribute read traffic across multiple database instances
- **Sharding**: Partition data by company, date range, or provider
- **Connection Pooling**: Efficient connection management under load
- **Query Optimization**: Indexed queries and materialized views

**Application Scaling**
- **Stateless Design**: API servers can be scaled horizontally
- **Load Balancing**: Distribute requests across multiple API instances
- **Caching Layers**: Redis for session storage and frequently accessed data
- **Async Processing**: Background jobs for data ingestion and calculations

**Frontend Scaling**
- **CDN Integration**: Static asset distribution
- **Code Splitting**: Load only required components
- **Service Workers**: Offline capability and caching
- **Progressive Loading**: Lazy load components and data

### Performance Optimization

**Data Access Patterns**
- **Bulk Operations**: Batch database operations for efficiency
- **Pagination**: Limit result sets for large datasets
- **Eager Loading**: Reduce N+1 queries with strategic joins
- **Materialized Views**: Pre-calculated aggregations for common queries

**Computation Efficiency**
- **Memoization**: Cache calculation results for repeated operations
- **Parallel Processing**: Concurrent data provider operations
- **Background Jobs**: Offload heavy computations from request cycles
- **Resource Pooling**: Reuse expensive resources (database connections, HTTP clients)

## Security Architecture

### Defense in Depth

The system implements multiple layers of security:

**Network Security**
- **HTTPS Encryption**: All traffic encrypted in transit
- **CORS Configuration**: Restricted cross-origin requests
- **Rate Limiting**: Prevent abuse and DoS attacks
- **IP Whitelisting**: Restrict access from approved networks

**Application Security**
- **Input Validation**: Comprehensive validation of all inputs
- **SQL Injection Prevention**: Parameterized queries and ORM usage
- **XSS Protection**: Content Security Policy and output encoding
- **CSRF Protection**: Token-based CSRF prevention

**Data Security**
- **Encryption at Rest**: Database encryption for sensitive data
- **Access Controls**: Role-based access to financial data
- **Audit Logging**: Comprehensive logging of data access and modifications
- **Data Retention**: Automated cleanup of expired data

## Deployment Architecture

### Containerization Strategy

The system uses Docker for consistent deployment across environments:

```yaml
# docker-compose.yml structure
services:
  frontend:          # React application (Nginx)
  backend:           # FastAPI application (Python)
  database:          # PostgreSQL with initialization
  redis:             # Caching and session storage
  nginx:             # Reverse proxy and load balancer
```

**Container Benefits**
- **Environment Consistency**: Same runtime across development, staging, and production
- **Scalability**: Easy horizontal scaling of services
- **Resource Isolation**: Controlled resource allocation
- **Deployment Simplicity**: Atomic deployments with rollback capability

### Infrastructure Requirements

**Minimum System Requirements**
- **CPU**: 2 cores for backend processing
- **Memory**: 4GB RAM for application and database
- **Storage**: 50GB for database and application files
- **Network**: 100 Mbps for external API calls

**Production Recommendations**
- **CPU**: 8+ cores for concurrent request handling
- **Memory**: 16GB+ RAM for database caching and application scaling
- **Storage**: 500GB+ SSD for database performance
- **Network**: 1 Gbps for high-throughput data ingestion

## Monitoring and Observability

### Application Monitoring

**Key Metrics**
- **Request Latency**: API response times and percentiles
- **Error Rates**: 4xx/5xx error rates by endpoint
- **Throughput**: Requests per second and concurrent users
- **Data Ingestion**: Records processed per minute, success rates

**Business Metrics**
- **User Engagement**: Active users, session duration
- **Data Quality**: Provider success rates, data freshness
- **Calculation Accuracy**: Validation against known benchmarks
- **Financial Coverage**: Companies and time periods available

### Operational Monitoring

**Infrastructure Metrics**
- **System Resources**: CPU, memory, disk usage
- **Database Performance**: Query times, connection pool usage
- **Network**: Bandwidth utilization, external API latency
- **Container Health**: Container restart rates, resource consumption

**Alerting Strategy**
- **Critical Alerts**: Service unavailability, data corruption
- **Warning Alerts**: High latency, elevated error rates
- **Informational**: Daily data ingestion summaries, usage reports
- **Escalation**: Automated escalation for unacknowledged critical alerts

This architecture provides a solid foundation for a scalable, maintainable, and secure equity valuation system while maintaining flexibility for future enhancements and integrations.