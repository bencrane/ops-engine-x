> ## Documentation Index
> Fetch the complete documentation index at: https://resend.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Managing Domains

> Visualize all the domains on the Resend Dashboard.

<Warning>
  Domain not verifying? [Try
  this](/knowledge-base/what-if-my-domain-is-not-verifying).
</Warning>

## Verifying a domain

Resend sends emails using a domain you own.

We recommend using subdomains (e.g., `updates.example.com`) to isolate your sending reputation and communicate your intent. Learn more about [using subdomains](/knowledge-base/is-it-better-to-send-emails-from-a-subdomain-or-the-root-domain).

In order to verify a domain, you must set two DNS entries:

1. [SPF](#what-are-spf-records): list of IP addresses authorized to send email on behalf of your domain
2. [DKIM](#what-are-dkim-records): public key used to verify email authenticity

These two DNS entries grant Resend permission to send email on your behalf. Once SPF and DKIM verify, you can optionally add a [DMARC record](/dashboard/domains/dmarc) to build additional trust with mailbox providers.

<Info>
  Resend requires you own your domain (i.e., not a shared or public domain).
</Info>

## View domain details

The [Domains dashboard](https://resend.com/domains) shows information about your domain name, its verification status, and history.

<img alt="Domain Details" src="https://mintcdn.com/resend/JHWt09hsc7E33HK2/images/dashboard-domains-resend.png?fit=max&auto=format&n=JHWt09hsc7E33HK2&q=85&s=feb6b86344d63199055cdaa7b15735fa" width="2992" height="1868" data-path="images/dashboard-domains-resend.png" />

<Info>
  Need specific help with a provider? View our [knowledge base DNS
  Guides](/knowledge-base).
</Info>

## What are SPF records

Sender Policy Framework (SPF) is an email authentication standard that allows you to list all the IP addresses that are authorized to send email on behalf of your domain.

The SPF configuration is made of a TXT record that lists the IP addresses approved by the domain owner. It also includes a MX record that allows the recipient to send bounce and complaint feedback to your domain.

<img alt="SPF Records" src="https://mintcdn.com/resend/JHWt09hsc7E33HK2/images/dashboard-domains-resend-spf.png?fit=max&auto=format&n=JHWt09hsc7E33HK2&q=85&s=630f500feba7768e05a69340e8a6dae5" width="2992" height="1868" data-path="images/dashboard-domains-resend-spf.png" />

## Custom Return Path

By default, Resend will use the `send` subdomain for the Return-Path address. You can change this by setting the optional `custom_return_path` parameter when [creating a domain](/api-reference/domains/create-domain) via the API or under **Advanced options** in the dashboard.

<img alt="Custom Return Path" src="https://mintcdn.com/resend/JHWt09hsc7E33HK2/images/dashboard-domains-resend-custom-return-path.png?fit=max&auto=format&n=JHWt09hsc7E33HK2&q=85&s=569a75fc160aad18116efc93bcebe148" width="3360" height="2100" data-path="images/dashboard-domains-resend-custom-return-path.png" />

For the API, optionally pass the custom return path parameter.

<CodeGroup>
  ```ts Node.js theme={"theme":{"light":"github-light","dark":"vesper"}}
  import { Resend } from 'resend';

  const resend = new Resend('re_xxxxxxxxx');

  resend.domains.create({ name: 'example.com', customReturnPath: 'outbound' });
  ```

  ```php PHP theme={"theme":{"light":"github-light","dark":"vesper"}}
  $resend = Resend::client('re_xxxxxxxxx');

  $resend->domains->create([
    'name' => 'example.com',
    'custom_return_path' => 'outbound'
  ]);
  ```

  ```python Python theme={"theme":{"light":"github-light","dark":"vesper"}}
  import resend

  resend.api_key = "re_xxxxxxxxx"

  params: resend.Domains.CreateParams = {
    "name": "example.com",
    "custom_return_path": "outbound"
  }

  resend.Domains.create(params)
  ```

  ```ruby Ruby theme={"theme":{"light":"github-light","dark":"vesper"}}
  Resend.api_key = ENV["RESEND_API_KEY"]

  params = {
    name: "example.com",
    custom_return_path: "outbound"
  }
  domain = Resend::Domains.create(params)
  puts domain
  ```

  ```go Go theme={"theme":{"light":"github-light","dark":"vesper"}}
  package main

  import "github.com/resend/resend-go/v3"

  func main() {
  	client := resend.NewClient("re_xxxxxxxxx")

  	params := &resend.CreateDomainRequest{
  		Name:             "example.com",
  		CustomReturnPath: "outbound",
  	}

  	domain, err := client.Domains.Create(params)
  }
  ```

  ```rust Rust theme={"theme":{"light":"github-light","dark":"vesper"}}
  use resend_rs::{types::CreateDomainOptions, Resend, Result};

  #[tokio::main]
  async fn main() -> Result<()> {
    let resend = Resend::new("re_xxxxxxxxx");

    let _domain = resend
      .domains
      .add(CreateDomainOptions::new("example.com").with_custom_return_path("outbound"))
      .await?;

    Ok(())
  }
  ```

  ```java Java theme={"theme":{"light":"github-light","dark":"vesper"}}
  import com.resend.*;

  public class Main {
      public static void main(String[] args) {
          Resend resend = new Resend("re_xxxxxxxxx");

          CreateDomainOptions params = CreateDomainOptions
                  .builder()
                  .name("example.com")
                  .customReturnPath("outbound")
                  .build();

          CreateDomainResponse domain = resend.domains().create(params);
      }
  }
  ```

  ```csharp .NET theme={"theme":{"light":"github-light","dark":"vesper"}}
  using Resend;

  IResend resend = ResendClient.Create( "re_xxxxxxxxx" ); // Or from DI

  var resp = await resend.DomainAddAsync( new DomainAddData {
     DomainName = "example.com",
     CustomReturnPath = "outbound"
  } );
  Console.WriteLine( "Domain Id={0}", resp.Content.Id );
  ```

  ```bash cURL theme={"theme":{"light":"github-light","dark":"vesper"}}
  curl -X POST 'https://api.resend.com/domains' \
       -H 'Authorization: Bearer re_xxxxxxxxx' \
       -H 'Content-Type: application/json' \
       -d $'{
    "name": "example.com",
    "custom_return_path": "outbound"
  }'
  ```
</CodeGroup>

Custom return paths must adhere to the following rules:

* Must be 63 characters or less
* Must start with a letter, end with a letter or number, and contain only letters, numbers, and hyphens

Avoid setting values that could undermine credibility (e.g. `testing`), as they may be exposed to recipients in some email clients.

## What are DKIM records

DomainKeys Identified Mail (DKIM) is an email security standard designed to make sure that an email that claims to have come from a specific domain was indeed authorized by the owner of that domain.

The DKIM configuration is made of a TXT record that contains a public key that is used to verify the authenticity of the email.

<img alt="DKIM Records" src="https://mintcdn.com/resend/JHWt09hsc7E33HK2/images/dashboard-domains-resend-dkim.png?fit=max&auto=format&n=JHWt09hsc7E33HK2&q=85&s=345d1dc6b7c138dbd92bd6928c634bd9" width="2992" height="1868" data-path="images/dashboard-domains-resend-dkim.png" />

## Understand a domain status

Domains can have different statuses, including:

* `not_started`: You've added a domain to Resend, but you haven't clicked on `Verify DNS Records` yet.
* `pending`: Resend is still trying to verify the domain.
* `verified`: Your domain is successfully verified for sending in Resend.
* `partially_verified`: One capability (send or receive) is verified while the other is still pending verification.
* `partially_failed`: The domain is verified but one of the features (send or receive) is not verified.
* `failed`: Resend was unable to detect the DNS records within 72 hours.
* `temporary_failure`: For a previously verified domain, Resend will periodically check for the DNS record required for verification. If at some point, Resend is unable to detect the record, the status would change to "Temporary Failure". Resend will recheck for the DNS record for 72 hours, and if it's unable to detect the record, the domain status would change to "Failure". If it's able to detect the record, the domain status would change to "Verified".

## Open and Click Tracking

Open and click tracking is disabled by default for all domains.

You can enable it manually or programmatically.

<img alt="Open and Click Tracking" src="https://mintcdn.com/resend/8slja5cHAobSwGo7/images/dashboard-domains-custom-tracking-domains.png?fit=max&auto=format&n=8slja5cHAobSwGo7&q=85&s=b94c649f1c22c899c144cd73ab5a8e73" width="1869" height="959" data-path="images/dashboard-domains-custom-tracking-domains.png" />

Learn more about [open and click tracking](/dashboard/domains/tracking).

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
