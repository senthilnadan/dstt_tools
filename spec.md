# Specification: DSTT Tools Architecture (v1.0)

## 1. Project Overview
* **Name:** `dstt-tools-core`
* **Role:** The foundational tool management and execution layer for the DSTT Kernel.
* **Architecture:** A tripartite system consisting of a **Library** (implementations), a **Registry** (catalog and categorization), and a **Provider** (execution bridge).
* **Design Philosophy:** Strict separation of concerns. Tools are grouped by logical categories. The system is static and predictable at runtime, initialized strictly during the bootstrap phase.

## 2. Core Invariants (Agent Guidelines)
1. **Categorical Resolution:** Tools are registered and resolved using a category and a name (e.g., `math.multiply`, `system.echo`). 
2. **Bootstrap Initialization:** The Library populates the Registry at startup. No runtime "on-the-fly" registration is required for this version.
3. **Stateless Provider:** The Tool Provider manages execution routing but holds no state. It delegates lookup to the Registry and execution to the Tool.
4. **No Framework Bloat:** Tool signatures are derived from native Python inspection or DSTT artifact analysis. No Pydantic or external validation models.

## 3. Component Architecture

### A. The Tool Implementations (`Library`)
The Library is the physical collection of tool definitions, grouped logically.
* **`UniversalTool` (Interface):** All tools must implement `execute(*inputs) -> Result` and `get_signature() -> Dict`.
* **`NativeTool`:** Wraps standard Python functions. Auto-inspects arguments for its signature.
* **`CompositeTool`:** Wraps a DSTT JSON structure. Extracts its signature by comparing required transition inputs against internally generated milestone artifacts.

### B. The Tool Registry (`Registry`)
The catalog that holds the mapping of categories to tools.
* **State:** Maintains an internal nested dictionary mapping: `{ category_name: { tool_name: UniversalTool } }`.
* **`register(category: str, name: str, tool: UniversalTool)`:** Adds a tool to a specific category during bootstrap.
* **`get_tool(category: str, name: str) -> UniversalTool`:** Retrieves a tool. Raises a clean error if the category or tool does not exist.
* **`list_categories() -> List[str]`:** Returns all registered categories.
* **`list_tools(category: str) -> List[str]`:** Returns the names of all tools within a specific category.
* **`export_manifest() -> List[Dict]`:** Iterates through all categories and tools to build the LLM signature manifest.

### C. The Tool Provider (`Provider`)
The bridge passed directly to the DSTT Kernel.
* **Dependency:** Initialized with an instance of the `Registry`.
* **`execute_transition(tool_path: str, *inputs) -> Result`:** * Parses the `tool_path` (e.g., "math.multiply" splits into category "math", name "multiply").
    * Retrieves the tool from the `Registry`.
    * Calls `tool.execute(*inputs)` and returns the result.

## 4. Bootstrap Flow
During system startup, the bootstrap script must:
1. Initialize an empty `Registry`.
2. Load the system `Library` (e.g., math tools, iteration tools).
3. Call `registry.register("math", "multiply", NativeTool(multiply_func))` for each tool.
4. Initialize the `Provider` with the populated `Registry`.
5. Pass the `Provider` to the DSTT Kernel.

## 5. The Manifest Specification (LLM Contract)
When `registry.export_manifest()` is called, it MUST output a flat JSON array formatted exactly like this. The agent must ensure the logic produces this schema:

```json
[
  {
    "category": "math",
    "tool": "multiply",
    "inputs": ["a", "b"],
    "outputs": ["result"]
  },
  {
    "category": "system",
    "tool": "echo",
    "inputs": ["value"],
    "outputs": ["result"]
  }
]


6. Implementation Requirements for the Agent
To bootstrap this architecture, generate the following:

The UniversalTool abstract base class.

The NativeTool and CompositeTool concrete implementations.

The Registry class with the specified categorization and manifest export methods.

The Provider class with the string-parsing execution method.

A bootstrap test script that creates a "math" category, registers an addition tool, and executes it via the Provider.


You are assisting me in building the `dstt-tools-core` package, which serves as the tool registry and execution provider for Appu's DSTT (Deterministic State Transition Tree) Kernel. 

I am starting with a completely empty folder. I have attached the `spec.md` file which contains the strict architectural invariants and component definitions. 

Please execute the following steps in order. Do not use Pydantic or any heavy validation frameworks; we are keeping this strictly minimal and using native Python capabilities.

### Step 1: Project Initialization
1. Create a Python virtual environment (`venv`) in the root folder.
2. Generate a `pyproject.toml` file to make this project buildable and distributable as `dstt-tools-core`. Include a minimal build system requirement (like `setuptools` or `hatchling`).
3. Set up the standard Python package directory structure (e.g., a `src/dstt_tools_core/` folder).

### Step 2: Core Implementation (Follow `spec.md`)
Create the following files and classes strictly adhering to the `spec.md` architecture:
1. `interfaces.py`: Define the `UniversalTool` base class/protocol.
2. `tools.py`: Implement the `NativeTool` (with `inspect` signature extraction) and a mock `CompositeTool` (for DSTT JSON structures).
3. `registry.py`: Implement the `Registry` class to handle categorization, storage, and the `export_manifest()` JSON generation.
4. `provider.py`: Implement the `Provider` class that takes a `Registry`, parses a `"category.tool_name"` string, and executes the tool.

### Step 3: Bootstrapping & Testing
1. Create a `system_lib.py` file that contains a few basic native Python functions (e.g., `multiply(a, b)`, `echo(value)`).
2. Create a `test_bootstrap.py` script at the root level that:
   - Initializes the `Registry`.
   - Registers the functions from `system_lib.py` into a "math" and "system" category using `NativeTool`.
   - Initializes the `Provider` with this Registry.
   - Executes a transition (e.g., `provider.execute_transition("math.multiply", 2, 3)`).
   - Prints the output of `registry.export_manifest()` to prove the signature extraction works.

Please provide the terminal commands for Step 1, followed by the code for the files in Steps 2 and 3.