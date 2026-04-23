> ## Documentation Index
> Fetch the complete documentation index at: https://resend.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Event Types

> List of supported event types and their payload.

## Email Events

<div>
  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#FF9592',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`email.bounced`](/webhooks/emails/bounced)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever the recipient's mail server **permanently rejected the
      email**.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#BAA7FF',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`email.clicked`](/webhooks/emails/clicked)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever the **recipient clicks on an email link**.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#FFCA16',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`email.complained`](/webhooks/emails/complained)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever the email was successfully **delivered, but the recipient
      marked it as spam**.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#3DD68C',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`email.delivered`](/webhooks/emails/delivered)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever Resend **successfully delivered the email** to the
      recipient's mail server.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#B5B3AD',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`email.delivery_delayed`](/webhooks/emails/delivery-delayed)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever the **email couldn't be delivered due to a temporary
      issue**. Delivery delays can occur, for example, when the recipient's
      inbox is full, or when the receiving email server experiences a transient
      issue.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#FF9592',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`email.failed`](/webhooks/emails/failed)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever the **email failed to send due to an error**. This event
      is triggered when there are issues such as invalid recipients, API key
      problems, domain verification issues, email quota limits, or other sending
      failures.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#70B8FF',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`email.opened`](/webhooks/emails/opened)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever the **recipient opened the email**.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#4CCCE6',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`email.received`](/webhooks/emails/received)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever Resend **successfully receives an email**.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#B5B2BC',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`email.scheduled`](/webhooks/emails/scheduled)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever the **email is scheduled to be sent**.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#B5B3AD',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`email.sent`](/webhooks/emails/sent)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever the **API request was successful**. Resend will attempt to
      deliver the message to the recipient's mail server.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#D4B3A5',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`email.suppressed`](/webhooks/emails/suppressed)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever the **email is suppressed** by Resend.
    </div>
  </div>
</div>

## Domain Events

<div>
  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#3DD68C',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`domain.created`](/webhooks/domains/created)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs when a **domain was successfully created**.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#70B8FF',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`domain.updated`](/webhooks/domains/updated)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs when a **domain was successfully updated**.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#FF9592',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`domain.deleted`](/webhooks/domains/deleted)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs when a **domain was successfully deleted**.
    </div>
  </div>
</div>

## Contact Events

<div>
  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#3DD68C',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`contact.created`](/webhooks/contacts/created)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever a **contact was successfully created**.
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      *Note: When importing multiple contacts using CSV, these events won't be
      triggered. [Contact support](https://resend.com/contact) if you have any
      questions.*
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#70B8FF',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`contact.updated`](/webhooks/contacts/updated)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever a **contact was successfully updated**.
    </div>
  </div>

  <div style={{ marginBottom: '32px' }}>
    <div>
      <span
        style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#FF9592',
      verticalAlign: 'middle',
      marginRight: '6px',
    }}
      />

      {' '}

      [`contact.deleted`](/webhooks/contacts/deleted)
    </div>

    <div style={{ marginLeft: '20px', marginTop: '4px' }}>
      Occurs whenever a **contact was successfully deleted**.
    </div>
  </div>
</div>
