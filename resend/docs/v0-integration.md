> ## Documentation Index
> Fetch the complete documentation index at: https://resend.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Send emails with v0 and Resend

> Learn how to add the Resend integration to your v0 project.

[v0](https://v0.dev) by Vercel is a platform for building web sites, tools, apps, and projects via chat. You can add Resend in a v0 project by asking the chat to add email sending with Resend.

## 1. Add your Resend API key

To use Resend with v0, you'll need to add a Resend API key, which you can create in the [Resend Dashboard](https://resend.com/api-keys).

<Note>
  Do not share your API key with others or expose it in the browser or other
  client-side code.
</Note>

<img src="https://mintcdn.com/resend/lyl6PQTYhtWhUjuS/images/v0-integration.png?fit=max&auto=format&n=lyl6PQTYhtWhUjuS&q=85&s=cb85c63c4d0bca95571920a08324432f" alt="adding the Resend integration to a v0 chat" width="3808" height="2128" data-path="images/v0-integration.png" />

## 2. Add a custom domain to your Resend account

By default, you can only send emails to your own email address.

To send emails to other email addresses:

1. Add a [custom domain to your Resend account](https://resend.com/domains).
2. Add the custom domain to the `from` field in the `resend` function in v0 (or ask the chat to update these fields).

Get more help adding a custom domain in [Resend's documentation](/dashboard/domains/introduction).
