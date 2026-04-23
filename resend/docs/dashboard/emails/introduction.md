> ## Documentation Index
> Fetch the complete documentation index at: https://resend.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Managing Emails

> Learn how to view and manage all sent emails on the Resend Dashboard.

## View email details

See all the metadata associated with an email, including the sender address, recipient address, subject, and more from the [Emails](https://resend.com/emails) page. Select any email to view its details.

<img alt="Email Details" src="https://mintcdn.com/resend/JHWt09hsc7E33HK2/images/dashboard-emails-item.png?fit=max&auto=format&n=JHWt09hsc7E33HK2&q=85&s=406e90f545d6b4f4289cd86311a2642a" width="3024" height="1888" data-path="images/dashboard-emails-item.png" />

Each email contains a **Preview**, **Plain Text**, and **HTML** version to visualize the content of your sent email in its various formats.

## Understand email events

Here are all the events that can be associated with an email:

* `bounced` - The recipient's mail server rejected the email. ([Learn more about bounced emails](/dashboard/emails/email-bounces))
* `canceled` - The scheduled email was canceled (by user).
* `clicked` - The recipient clicked on a link in the email.
* `complained` - The email was successfully delivered to the recipient's mail server, but the recipient marked it as spam.
* `delivered` - Resend successfully delivered the email to the recipient's mail server.
* `delivery_delayed` - The email couldn't be delivered to the recipient's mail server because a temporary issue occurred. Delivery delays can occur, for example, when the recipient's inbox is full, or when the receiving email server experiences a transient issue.
* `failed` - The email failed to be sent.
* `opened` - The recipient opened the email. ([Open rates are not always accurate](/knowledge-base/why-are-my-open-rates-not-accurate))
* `queued` - The email created from Broadcasts or Batches is queued for delivery.
* `scheduled` - The email is scheduled for delivery.
* `sent` - The email was sent successfully.
* `suppressed` - The email was not sent because the recipient is on the suppression list. ([Learn more about the suppression list](/knowledge-base/why-are-my-emails-landing-on-the-suppression-list))

## Share email link

You can share a public link of a sent email, which is valid for 48 hours. Anyone with the link can visualize the email.

To share a link, click on the **dropdown menu** <Icon icon="ellipsis" iconType="solid" />, and select **Share email**.

<img alt="Email - Share Link Option" src="https://mintcdn.com/resend/JHWt09hsc7E33HK2/images/dashboard-emails-share-option.png?fit=max&auto=format&n=JHWt09hsc7E33HK2&q=85&s=1e3019a33d90161bc41a77817e2a54c5" width="3024" height="1888" data-path="images/dashboard-emails-share-option.png" />

Then copy the URL and share it with your team members.

<img alt="Email - Share Link Modal" src="https://mintcdn.com/resend/JHWt09hsc7E33HK2/images/dashboard-emails-share-modal.png?fit=max&auto=format&n=JHWt09hsc7E33HK2&q=85&s=467d298ee78312a1f1b8356ea61457e5" width="3024" height="1888" data-path="images/dashboard-emails-share-modal.png" />

Anyone with the link can visualize the email without authenticating for 48 hours.

<img alt="Email - Share Link Item" src="https://mintcdn.com/resend/JHWt09hsc7E33HK2/images/dashboard-emails-share-item.png?fit=max&auto=format&n=JHWt09hsc7E33HK2&q=85&s=05c438ac1b5e0721475b3f028a6f6934" width="3024" height="1888" data-path="images/dashboard-emails-share-item.png" />

## See associated logs

You can check all the logs associated with an email. This will help you troubleshoot any issues with the request itself.

To view the logs, click on the dropdown menu, and select "View log".

<img alt="Email - View Logs Option" src="https://mintcdn.com/resend/JHWt09hsc7E33HK2/images/dashboard-emails-log-option.png?fit=max&auto=format&n=JHWt09hsc7E33HK2&q=85&s=ad69ba9d638fe43f62974a0d76b1e01e" width="3024" height="1888" data-path="images/dashboard-emails-log-option.png" />

This will take you to logs, where you can see all the logs associated with the email.

<img alt="Email - View Logs Item" src="https://mintcdn.com/resend/JHWt09hsc7E33HK2/images/dashboard-emails-log-item.png?fit=max&auto=format&n=JHWt09hsc7E33HK2&q=85&s=936f066559e1ae477523be37aa959f90" width="3024" height="1888" data-path="images/dashboard-emails-log-item.png" />

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
