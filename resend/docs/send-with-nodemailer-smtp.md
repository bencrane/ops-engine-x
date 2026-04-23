> ## Documentation Index
> Fetch the complete documentation index at: https://resend.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Send emails using Nodemailer with SMTP

> Learn how to send your first email using Nodemailer with SMTP.

## Prerequisites

To get the most out of this guide, you'll need to:

* [Create an API key](https://resend.com/api-keys)
* [Verify your domain](https://resend.com/domains)

## 1. Install

Get the [Nodemailer](https://www.npmjs.com/package/nodemailer) package.

<CodeGroup>
  ```bash npm theme={"theme":{"light":"github-light","dark":"vesper"}}
  npm install nodemailer
  ```

  ```bash yarn theme={"theme":{"light":"github-light","dark":"vesper"}}
  yarn add nodemailer
  ```

  ```bash pnpm theme={"theme":{"light":"github-light","dark":"vesper"}}
  pnpm add nodemailer
  ```

  ```bash bun theme={"theme":{"light":"github-light","dark":"vesper"}}
  bun add nodemailer
  ```
</CodeGroup>

## 2. Send email using SMTP

When configuring your SMTP integration, you'll need to use the following credentials:

* **Host**: `smtp.resend.com`
* **Port**: `465`
* **Username**: `resend`
* **Password**: `YOUR_API_KEY`

Then use these credentials to create a transport:

```js index.ts theme={"theme":{"light":"github-light","dark":"vesper"}}
import nodemailer from 'nodemailer';

async function main() {
  const transporter = nodemailer.createTransport({
    host: 'smtp.resend.com',
    secure: true,
    port: 465,
    auth: {
      user: 'resend',
      pass: 're_xxxxxxxxx',
    },
  });

  const info = await transporter.sendMail({
    from: 'onboarding@resend.dev',
    to: 'delivered@resend.dev',
    subject: 'Hello World',
    html: '<strong>It works!</strong>',
  });

  console.log('Message sent: %s', info.messageId);
}

main().catch(console.error);
```

## 3. Try it yourself

<Card title="Nodemailer SMTP Example" icon="arrow-up-right-from-square" href="https://github.com/resend/resend-nodemailer-smtp-example">
  See the full source code.
</Card>
