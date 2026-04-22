# Code execution tool

Claude can analyze data, create visualizations, perform complex calculations, run system commands, create and edit files, and process uploaded files directly within the API conversation. The code execution tool allows Claude to run Bash commands and manipulate files in a secure, sandboxed environment.

Code execution is free when used with web search or web fetch. When web_search_20260209 or web_fetch_20260209 is included in your request, there are no additional charges for code execution tool calls beyond standard token costs.

This feature is not eligible for Zero Data Retention (ZDR).

## Model compatibility

The code execution tool (code_execution_20250825) is available on all active Claude models including Opus 4.6, Sonnet 4.6, Sonnet 4.5, Opus 4.5, Opus 4.1, Opus 4, Sonnet 4, Haiku 4.5, and deprecated models Sonnet 3.7 and Haiku 3.5.

## Platform availability

Code execution is available on Claude API (Anthropic) and Microsoft Azure AI Foundry. Not currently available on Amazon Bedrock or Google Vertex AI.

## Quick start

```shell
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-opus-4-6",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"}],
    "tools": [{"type": "code_execution_20250825", "name": "code_execution"}]
  }'
```

## How code execution works

1. Claude evaluates whether code execution would help answer your question
2. The tool provides Bash commands and file operations capabilities
3. All operations run in a secure sandbox environment
4. Claude provides results with any generated charts, calculations, or analysis

## Tool definition

```json
{
  "type": "code_execution_20250825",
  "name": "code_execution"
}
```

When provided, Claude gains access to two sub-tools:
- **bash_code_execution**: Run shell commands
- **text_editor_code_execution**: View, create, and edit files

## Capabilities

- **Execute Bash commands**: Run shell commands, install packages, check system info
- **Create and edit files**: Create config files, scripts, edit existing files
- **Upload and analyze files**: Process CSV, Excel, JSON, images via the Files API
- **Retrieve generated files**: Download files Claude creates during execution

## Containers

### Runtime environment
- Python version: 3.11.12
- OS: Linux-based container (x86_64)

### Resource limits
- Memory: 5GiB RAM
- Disk: 5GiB workspace storage
- CPU: 1 CPU

### Networking and security
- Internet access: Completely disabled
- Sandbox isolation: Full isolation from host system
- File access: Limited to workspace directory
- Expiration: Containers expire 30 days after creation

### Pre-installed libraries
- Data Science: pandas, numpy, scipy, scikit-learn, statsmodels
- Visualization: matplotlib, seaborn
- File Processing: pyarrow, openpyxl, xlsxwriter, pillow, pypdf, pdfplumber, reportlab
- Math: sympy, mpmath
- Utilities: tqdm, python-dateutil, pytz, sqlite, ripgrep

### Container reuse

Reuse containers across requests by providing the container ID from a previous response, maintaining created files between requests.

## Usage and pricing

Code execution is free when used with web_search_20260209 or web_fetch_20260209. Otherwise:

- Execution time has a minimum of 5 minutes
- Each organization receives 1,550 free hours per month
- Additional usage: $0.05 per hour, per container

## Programmatic tool calling

The code execution tool powers programmatic tool calling, allowing Claude to write code that calls your custom tools within the execution container. Set `allowed_callers: ["code_execution_20250825"]` on your tools to enable this.
