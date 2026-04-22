# Computer use tool

Claude can interact with computer environments through the computer use tool, which provides screenshot capabilities and mouse/keyboard control for autonomous desktop interaction.

Computer use is in beta and requires a beta header:
- "computer-use-2025-11-24" for Claude Opus 4.6, Claude Sonnet 4.6, Claude Opus 4.5
- "computer-use-2025-01-24" for Sonnet 4.5, Haiku 4.5, Opus 4.1, Sonnet 4, Opus 4, and Sonnet 3.7 (deprecated)

This feature is in beta and is not eligible for Zero Data Retention (ZDR).

## Model compatibility

| Model | Tool Version | Beta Flag |
|---|---|---|
| Claude Opus 4.6, Sonnet 4.6, Opus 4.5 | computer_20251124 | computer-use-2025-11-24 |
| All other supported models | computer_20250124 | computer-use-2025-01-24 |

## Security considerations

- Use a dedicated virtual machine or container with minimal privileges
- Avoid giving access to sensitive data or account login information
- Limit internet access to an allowlist of domains
- Ask a human to confirm decisions with meaningful real-world consequences

## Quick start

```shell
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: computer-use-2025-11-24" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "tools": [
      {"type": "computer_20251124", "name": "computer", "display_width_px": 1024, "display_height_px": 768, "display_number": 1},
      {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"},
      {"type": "bash_20250124", "name": "bash"}
    ],
    "messages": [{"role": "user", "content": "Save a picture of a cat to my desktop."}]
  }'
```

## How computer use works

1. Provide Claude with the computer use tool and a user prompt
2. Claude decides to use the computer use tool
3. Extract tool input, evaluate on a computer, and return results
4. Claude continues calling tools until task is completed

## Available actions

### Basic actions (all versions)
- **screenshot** - Capture the current display
- **left_click** - Click at coordinates [x, y]
- **type** - Type text string
- **key** - Press key or key combination
- **mouse_move** - Move cursor to coordinates

### Enhanced actions (computer_20250124)
- **scroll** - Scroll in any direction with amount control
- **left_click_drag** - Click and drag between coordinates
- **right_click**, **middle_click** - Additional mouse buttons
- **double_click**, **triple_click** - Multiple clicks
- **left_mouse_down**, **left_mouse_up** - Fine-grained click control
- **hold_key** - Hold down a key for a specified duration
- **wait** - Pause between actions

### Enhanced actions (computer_20251124)
- All actions from computer_20250124
- **zoom** - View a specific screen region at full resolution (requires enable_zoom: true)

## Tool parameters

| Parameter | Required | Description |
|---|---|---|
| type | Yes | Tool version |
| name | Yes | Must be "computer" |
| display_width_px | Yes | Display width in pixels |
| display_height_px | Yes | Display height in pixels |
| display_number | No | Display number for X11 |
| enable_zoom | No | Enable zoom action (computer_20251124 only) |

## Prompting tips

- Specify simple, well-defined tasks with explicit instructions
- Prompt Claude to take screenshots after each step and verify outcomes
- Use keyboard shortcuts for tricky UI elements
- Include example screenshots for repeatable tasks
- Use system prompt for explicit tips on known tasks

## Limitations

- **Latency**: May be too slow for real-time human-AI interactions
- **Computer vision accuracy**: May make mistakes with coordinates
- **Tool selection**: May hallucinate when selecting tools
- **Scrolling**: Improved in Claude 4 models with dedicated scroll actions
- **Account creation**: Limited ability on social media platforms
- **Prompt injection**: May follow commands found in content on webpages

## Pricing

- System prompt overhead: 466-499 tokens
- Computer use tool: 735 tokens per tool definition
- Additional costs: Screenshot images (Vision pricing) and tool execution results
