> ## Documentation Index
> Fetch the complete documentation index at: https://resend.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Send emails with AWS Lambda

> Learn how to send your first email using AWS Lambda.

## Prerequisites

To get the most out of this guide, you'll need to:

* [Create an API key](https://resend.com/api-keys)
* [Verify your domain](https://resend.com/domains)

## 1. Create a AWS Lambda function

Go to [aws.amazon.com](https://aws.amazon.com) and create a new Lambda function using the Node.js 20.x or later runtime.

<img alt="AWS Lambda - New Function" src="https://mintcdn.com/resend/ABWmVTZIHGIFNTFD/images/aws-lambda-new-function.png?fit=max&auto=format&n=ABWmVTZIHGIFNTFD&q=85&s=324a1181f685affebb1f50b18765538c" width="3414" height="1886" data-path="images/aws-lambda-new-function.png" />

## 2. Edit the handler function

Paste the following code into the browser editor:

```js index.mjs theme={"theme":{"light":"github-light","dark":"vesper"}}
const RESEND_API_KEY = 're_xxxxxxxxx';

export const handler = async (event) => {
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${RESEND_API_KEY}`,
    },
    body: JSON.stringify({
      from: 'Acme <onboarding@resend.dev>',
      to: ['delivered@resend.dev'],
      subject: 'hello world',
      html: '<strong>it works!</strong>',
    }),
  });

  if (res.ok) {
    const data = await res.json();

    return {
      statusCode: 200,
      body: data,
    };
  }
};
```

## 3. Deploy and send email

Click on `Deploy` and then `Test` at the top of the screen.

<img alt="AWS Lambda - Edit Function" src="https://mintcdn.com/resend/ABWmVTZIHGIFNTFD/images/aws-lambda-edit-function.png?fit=max&auto=format&n=ABWmVTZIHGIFNTFD&q=85&s=0393dc19bce3c93881bf4b433024c40b" width="3414" height="1886" data-path="images/aws-lambda-edit-function.png" />

## 4. Try it yourself

<Card title="AWS Lambda Example" icon="arrow-up-right-from-square" href="https://github.com/resend/resend-aws-lambda-example">
  See the full source code.
</Card>
