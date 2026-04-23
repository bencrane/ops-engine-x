> ## Documentation Index
> Fetch the complete documentation index at: https://resend.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Introduction

> Visualize all the API Keys on the Resend Dashboard.

## What is an API Key

API Keys are secret tokens used to authenticate your requests. They are unique to your account and should be kept confidential.

## Add API Key

You can create a new API Key from the [API Key Dashboard](https://resend.com/api-keys), the [API](/api-reference/api-keys/create-api-key), or the [Resend CLI](/cli).

1. Click **Create API Key**.
2. Give your API Key a name (maximum 50 characters).
3. Select **Full access** or **Sending access** as the permission.
4. If you select **Sending access**, you can choose the domain you want to restrict access to.

<img alt="Add API Key" src="https://mintcdn.com/resend/ABWmVTZIHGIFNTFD/images/dashboard-api-keys-add.png?fit=max&auto=format&n=ABWmVTZIHGIFNTFD&q=85&s=1ecfaf7a2d2a780b826f941078e427b5" height={450} width={720} data-path="images/dashboard-api-keys-add.png" />

<Note>
  For security reasons, you can only view the API Key once. Learn more about
  [API key best practices](/knowledge-base/how-to-handle-api-keys).
</Note>

## Set API Key permissions

There are two different permissions of API Keys:

1. **Full access**: grants access to create, delete, get, and update any resource.
2. **Sending access**: grants access only to send emails.

With API Key permissions, you can isolate different application actions to different API Keys. Using multiple keys, you can view logs per key, detect possible abuse, and control the damage that may be done accidentally or maliciously.

## View all API Keys

The [API Dashboard](https://resend.com/api-keys) shows you all the API Keys you have created along with their details, including the **last time you used** an API Key.

Different color indicators let you quickly scan and detect which API Keys are being used and which are not.

<img alt="View All API Keys" src="https://mintcdn.com/resend/ABWmVTZIHGIFNTFD/images/dashboard-api-keys-view-all.jpg?fit=max&auto=format&n=ABWmVTZIHGIFNTFD&q=85&s=f195ef7f60a110407e2739f30c10ca2a" width="2584" height="980" data-path="images/dashboard-api-keys-view-all.jpg" />

## Edit API Key details

After creating an API Key, you can edit the following details:

* Name
* Permission
* Domain

To edit an API Key, click the **More options** <Icon icon="ellipsis" iconType="solid" /> button and then **Edit API Key**.

<img alt="View Inactive API Key" src="https://mintcdn.com/resend/ABWmVTZIHGIFNTFD/images/dashboard-api-keys-edit.jpeg?fit=max&auto=format&n=ABWmVTZIHGIFNTFD&q=85&s=7abe8e055cf311a7f66a40477db7946a" width="1752" height="878" data-path="images/dashboard-api-keys-edit.jpeg" />

<Info>You cannot edit an API Key value after it has been created.</Info>

## Delete inactive API Keys

If an API Key **hasn't been used in the last 30 days**, consider deleting it to keep your account secure.

<img alt="View Inactive API Key" src="https://mintcdn.com/resend/ABWmVTZIHGIFNTFD/images/dashboard-api-keys-view-inactive.jpg?fit=max&auto=format&n=ABWmVTZIHGIFNTFD&q=85&s=fa99650454696902100e03b669d3a9c1" width="2584" height="980" data-path="images/dashboard-api-keys-view-inactive.jpg" />

You can delete an API Key by clicking the **More options** <Icon icon="ellipsis" iconType="solid" /> button and then **Remove API Key**.

<img alt="Delete API Key" src="https://mintcdn.com/resend/ABWmVTZIHGIFNTFD/images/dashboard-api-keys-remove.jpeg?fit=max&auto=format&n=ABWmVTZIHGIFNTFD&q=85&s=9fc76ff5dc4cd38f465539cd3a435706" width="2649" height="980" data-path="images/dashboard-api-keys-remove.jpeg" />

## View API Key logs

When visualizing an active API Key, you can see the **total number of requests** made to the key. For more detailed logging information, select the underlined number of requests to view all logs for that API Key.

<img alt="View Active API Key" src="https://mintcdn.com/resend/ABWmVTZIHGIFNTFD/images/dashboard-api-keys-view-active.jpg?fit=max&auto=format&n=ABWmVTZIHGIFNTFD&q=85&s=e0c0584545565e1e78e460b240d2c221" width="2584" height="980" data-path="images/dashboard-api-keys-view-active.jpg" />

## Export your data

Admins can download your data in CSV format for the following resources:

* Emails
* Broadcasts
* Contacts
* Segments
* Domains
* Logs
* API keys

<Info>Currently, exports are limited to admin users of your team.</Info>

To start, apply filters to your data and click on the "Export" button. Confirm your filters before exporting your data.

<video autoPlay muted loop playsinline className="w-full aspect-video" src="https://mintcdn.com/resend/OWNnQaVDyqcGyhhN/images/exports.mp4?fit=max&auto=format&n=OWNnQaVDyqcGyhhN&q=85&s=1149ee4e83b4414e75a0ecaa92774c38" data-path="images/exports.mp4" />

If your exported data includes 1,000 items or less, the export will download immediately. For larger exports, you'll receive an email with a link to download your data.

All admins on your team can securely access the export for 7 days. Unavailable exports are marked as "Expired."

<Note>
  All exports your team creates are listed in the
  [Exports](https://resend.com/exports) page under **Settings** > **Team** >
  **Exports**. Select any export to view its details page. All members of your
  team can view your exports, but only admins can download the data.
</Note>
