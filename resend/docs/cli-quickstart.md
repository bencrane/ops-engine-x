> ## Documentation Index
> Fetch the complete documentation index at: https://resend.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Send emails with Resend CLI

> Learn how to send your first email using the Resend CLI.

## Prerequisites

To get the most out of this guide, you'll need to:

* [Create an API key](https://resend.com/api-keys)
* [Verify your domain](https://resend.com/domains)

## 1. Install

<Tabs>
  <Tab title="cURL">
    ```bash theme={"theme":{"light":"github-light","dark":"vesper"}}
    curl -fsSL https://resend.com/install.sh | bash
    ```
  </Tab>

  <Tab title="npm">
    ```bash theme={"theme":{"light":"github-light","dark":"vesper"}}
    npm install -g resend-cli
    ```
  </Tab>

  <Tab title="Homebrew">
    ```bash theme={"theme":{"light":"github-light","dark":"vesper"}}
    brew install resend/cli/resend
    ```
  </Tab>

  <Tab title="PowerShell (Windows)">
    ```powershell theme={"theme":{"light":"github-light","dark":"vesper"}}
    irm https://resend.com/install.ps1 | iex
    ```
  </Tab>
</Tabs>

## 2. Authenticate

```bash theme={"theme":{"light":"github-light","dark":"vesper"}}
resend login
```

## 3. Send email

```bash theme={"theme":{"light":"github-light","dark":"vesper"}}
resend emails send \
  --from "Acme <onboarding@resend.dev>" \
  --to delivered@resend.dev \
  --subject "Hello World" \
  --text "Sent from my terminal."
```

## Next steps

<Card title="CLI Reference" icon="terminal" href="/cli">
  Explore the full command reference, authentication options, and CI/CD
  examples.
</Card>
