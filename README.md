# Business Backend

FastAPI base project with PostgreSQL database, LLM integration, and ML capabilities.

## Structure

```
business_backend/
├── main.py                 # FastAPI app entry point
├── container.py            # Dependency Injection (aioinject)
│
├── config/
│   └── settings.py         # Pydantic BaseSettings (env vars)
│
├── database/
│   ├── connection.py       # AsyncEngine (SQLAlchemy 2.0)
│   ├── session.py          # Async session factory
│   └── models/
│       └── product_stock.py  # ORM models
│
├── llm/                    # [OPTIONAL] LLM integration
│   ├── provider.py         # OpenAI via LangChain
│   └── tools/
│       └── product_search_tool.py  # LangChain tools
│
├── ml/                     # [OPTIONAL] Machine Learning
│   ├── preprocessing/      # Data transformation
│   │   ├── base.py         # BasePreprocessor (abstract)
│   │   └── image_preprocessor.py
│   ├── models/             # Model wrappers
│   │   ├── base.py         # BaseModel (abstract)
│   │   ├── registry.py     # Model registry (MLflow pattern)
│   │   └── image_classifier.py
│   ├── serving/            # Inference service
│   │   └── inference_service.py
│   └── training/           # Re-training
│       ├── trainer.py      # Training logic
│       └── experiment_tracker.py  # MLflow pattern
│
├── services/
│   ├── tenant_data_service.py  # CSV data (existing)
│   ├── product_service.py      # DB CRUD operations
│   └── search_service.py       # LLM orchestration
│
├── api/graphql/
│   ├── types.py            # Strawberry GraphQL types
│   └── queries.py          # GraphQL queries
│
└── domain/
    └── product_schemas.py  # Pydantic schemas
```

## Environment Variables

```env
# Database (required)
PG_URL=postgresql+asyncpg://user:pass@localhost:5432/db_name

# LLM (optional)
OPENAI_API_KEY=sk-...
LLM_ENABLED=true   # Set to false to disable LLM
```
    
## Testing Changes
    
To test the recent changes (Computer Endpoint), including the flow of fetching details by ID:
    
1. **Start the application** (Ensure Docker is running for the database):
   ```bash
   ./start.sh
   ```
    
2. **Simulate Frontend Flow**:
    
   **Step A: Create 3 Computers**
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"brand": "Dell", "code": "SKU-LAPTOP-let01", "price": 1200.00, "description": "Laptop 1"}' http://localhost:9000/api/computers
   curl -X POST -H "Content-Type: application/json" -d '{"brand": "HP", "code": "SKU-LAPTOP-al01", "price": 800.00, "description": "Laptop 2"}' http://localhost:9000/api/computers
   curl -X POST -H "Content-Type: application/json" -d '{"brand": "Apple", "code": "SKU-LAPTOP-asu01", "price": 2000.00, "description": "Laptop 3"}' http://localhost:9000/api/computers
   ```
    
   **Step B: Get All IDs**
   ```bash
   curl -s http://localhost:9000/api/computers
   # Copy one "id" from the response, e.g., "550e8400-e29b-41d4-a716-446655440000"
   ```
    
   **Step C: Get Details for ONE ID**
   ```bash
   # Replace <ID> with the actual UUID
   curl http://localhost:9000/api/computers/<ID>
   ```

## Run

The easiest way to run the project (including database, dependencies, and environment setup) is:

```bash
./start.sh
```

or manually:

```bash
poetry run python -m business_backend.main --port 9000
```

- GraphiQL UI: http://localhost:9000/graphql
- API Docs: http://localhost:9000/docs
- Health: http://localhost:9000/health

## API Usage

### GraphQL
- Endpoint: `http://localhost:9000/graphql`
- UI: GraphiQL enabled at the same URL.

### REST
- **POST /api/detect**: Image Recognition
  - Upload an image to identify the product.
  - Body: `multipart/form-data` with field `file`.
  - Response: JSON with prediction and confidence.
  
  Example:
  ```bash
  curl -X POST -F "file=@image.jpg" http://localhost:9000/api/detect
  ```
    
  ### Computers
  - **GET /api/computers**: List all computers.
  - **GET /api/computers/{id}**: Get details of a specific computer.
  - **POST /api/computers**: Create a new computer.
    - Body (JSON): `{"brand": "Str", "price": Float, "description": "Str"}`
    
    Example:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"brand": "Dell", "price": 1200.50, "description": "XPS 15"}' http://localhost:9000/api/computers
    ```

## GraphQL Queries

| Query                     | Description             |
| ------------------------- | ----------------------- |
| `getFaqs(tenant)`         | Get FAQs from CSV       |
| `getDocuments(tenant)`    | Get documents from CSV  |
| `products(limit, offset)` | List products from DB   |
| `product(id)`             | Get product by UUID     |
| `searchProducts(name)`    | Search products by name |
| `semanticSearch(query)`   | LLM-powered search      |

### Examples

```graphql
# List products
query {
  products(limit: 10) {
    productName
    quantityAvailable
    stockStatus
  }
}

# Semantic search
query {
  semanticSearch(query: "Do you have milk in stock?") {
    answer
    productsFound {
      productName
      quantityAvailable
    }
  }
}
```

## Adding New Services

### 1. Create Service

```python
# services/my_service.py
class MyService:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def my_method(self):
        async with self.session_factory() as session:
            # SQLAlchemy ORM queries here
            pass
```

### 2. Register in Container

```python
# container.py
from business_backend.services.my_service import MyService

async def create_my_service(session_factory) -> MyService:
    return MyService(session_factory)

def providers():
    # ... existing providers
    providers_list.append(aioinject.Singleton(create_my_service))
```

### 3. Add GraphQL Query

```python
# api/graphql/queries.py
@strawberry.field
@inject
async def my_query(
    self,
    my_service: Annotated[MyService, Inject],
) -> MyType:
    return await my_service.my_method()
```

## Adding New Models

### 1. Create SQLAlchemy Model

```python
# database/models/my_model.py
from sqlalchemy.orm import Mapped, mapped_column
from business_backend.database.models.product_stock import Base

class MyModel(Base):
    __tablename__ = "my_table"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
```

### 2. Export in `__init__.py`

```python
# database/models/__init__.py
from business_backend.database.models.my_model import MyModel
```

## Removing LLM Module

To remove LLM functionality:

### Option 1: Disable via Environment

```env
LLM_ENABLED=false
```

The `semanticSearch` query will use fallback (direct DB search).

### Option 2: Remove Completely

1. Delete `llm/` directory
2. Delete `services/search_service.py`
3. Update `container.py`:

```python
# Remove these lines:
from business_backend.llm.provider import LLMProvider, create_llm_provider
from business_backend.services.search_service import SearchService

# Remove these providers:
# providers_list.append(aioinject.Singleton(create_llm_provider_instance))
# providers_list.append(aioinject.Singleton(create_search_service))
```

4. Update `api/graphql/queries.py`:
   - Remove `SearchService` import
   - Remove `semantic_search` query

## Adding LangChain Tools

```python
# llm/tools/my_tool.py
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    param: str = Field(description="Description for LLM")

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "What this tool does (for LLM)"
    args_schema: type[BaseModel] = MyToolInput

    async def _arun(self, param: str) -> str:
        # Tool logic here
        return "result"
```

Then bind in `search_service.py`:

```python
model_with_tools = self.llm_provider.bind_tools([
    self.search_tool,
    my_new_tool,  # Add here
])
```

## Architecture

```
Request → GraphQL → Service → Database (SQLAlchemy ORM)
                         ↓
                   LLM Provider → LangChain Tools → Service
                         ↓
                   ML Module → Inference/Training → Models
```

- **Dependency Injection**: aioinject container
- **Database**: SQLAlchemy 2.0 async with PostgreSQL
- **GraphQL**: Strawberry with aioinject extension
- **LLM**: LangChain with OpenAI (tool calling)
- **ML**: Preprocessing, serving, training (optional)

---

## Machine Learning Module

The `ml/` module provides ML capabilities for preprocessing, inference, and training.

### ML Structure

| Module           | Purpose                             |
| ---------------- | ----------------------------------- |
| `preprocessing/` | Transform raw data to model input   |
| `models/`        | Model wrappers and registry         |
| `serving/`       | Inference service                   |
| `training/`      | Re-training and experiment tracking |

### ML Inference Flow

```
1. Register model in registry
2. InferenceService.predict(model_name, data)
   └─→ Registry.load(model_name)
       └─→ Model.predict(preprocessed_data)
           └─→ PredictionResult
```

### ML Training Flow

```
1. Create Trainer with ExperimentTracker
2. Trainer.train(model, dataset, config)
   └─→ ExperimentTracker.start_run()
       └─→ Training loop (log metrics per epoch)
           └─→ save_checkpoint()
               └─→ ExperimentTracker.end_run()
```

### Adding a New ML Model

#### 1. Create Model Class

```python
# ml/models/my_model.py
from business_backend.ml.models.base import BaseModel

class MyModel(BaseModel):
    model_type: str = "image"  # or "text", "tabular"
    input_shape: tuple = (224, 224, 3)

    async def load(self, path):
        # Here your code for loading model
        pass

    async def predict(self, data):
        # Here your code for inference
        return {"prediction": result, "confidence": 0.95}
```

#### 2. Create Preprocessor (if needed)

```python
# ml/preprocessing/my_preprocessor.py
from business_backend.ml.preprocessing.base import BasePreprocessor

class MyPreprocessor(BasePreprocessor):
    async def process(self, data):
        # Here your code for preprocessing
        pass

    async def process_batch(self, data_list):
        # Here your code for batch preprocessing
        pass

    def validate(self, data):
        # Here your code for validation
        pass
```

#### 3. Register and Use

```python
from business_backend.ml.models.registry import ModelRegistry, ModelStage
from business_backend.ml.models.my_model import MyModel
from business_backend.ml.serving.inference_service import InferenceService

# Register
registry = ModelRegistry()
registry.register(
    name="my_model",
    model_class=MyModel,
    model_path="path/to/weights.h5",
    stage=ModelStage.PRODUCTION,
)

# Inference
service = InferenceService(registry)
result = await service.predict("my_model", input_data)
```

### Training a Model

```python
from business_backend.ml.training.trainer import Trainer, TrainConfig
from business_backend.ml.training.experiment_tracker import ExperimentTracker

# Setup
tracker = ExperimentTracker(artifact_location="./experiments")
trainer = Trainer(experiment_tracker=tracker)

# Configure
config = TrainConfig(
    epochs=50,
    batch_size=32,
    learning_rate=0.001,
    early_stopping=True,
)

# Train
result = await trainer.train(
    model=my_model,
    train_data=train_dataset,
    config=config,
    validation_data=val_dataset,
)

# Evaluate
eval_result = await trainer.evaluate(my_model, test_dataset)
```

### Removing ML Module

To remove ML functionality completely:

1. Delete `ml/` directory
2. Remove ML imports from `container.py` (if any)
3. Remove ML GraphQL queries (if any)

The module is self-contained and has no dependencies on other modules.
