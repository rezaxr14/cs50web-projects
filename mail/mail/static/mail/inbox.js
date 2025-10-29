document.addEventListener('DOMContentLoaded', function () {

  // Nav buttons
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email()); // fixed? PointerEvent issue

  // Send email form
  const form = document.querySelector('#compose-form');
  if (form) {
    form.addEventListener('submit', send_email);
  } else {
    console.warn('compose-form not found in DOM');
  }

  // Default to inbox
  load_mailbox('inbox');
});


// Open compose view, optionally pre-filling for reply
function compose_email(recipients = '', subject = '', body = '') {
  // Hide mailbox
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear dynamic detail views if any
  document.querySelectorAll('.detail-view').forEach(el => el.remove());

  // Fill in form
  document.querySelector('#compose-recipients').value = recipients;
  document.querySelector('#compose-subject').value = subject;
  document.querySelector('#compose-body').value = body;

  try { document.querySelector('#compose-recipients').focus(); } catch (e) {}
}


// Send new email
function send_email(e) {
  e.preventDefault();

  const to = document.querySelector('#compose-recipients').value.trim();
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  if (!to) {
    alert('Please enter at least one recipient.');
    return;
  }

  console.log('Sending email to:', to);

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: to,
      subject: subject,
      body: body
    })
  })
    .then(res => res.json())
    .then(result => {
      if (result.error) {
        alert(result.error);
        return;
      }
      setTimeout(() => load_mailbox('sent'), 150); // small delay
    })
    .catch(err => console.error('Send failed:', err));
}


// Load a mailbox
function load_mailbox(mailbox) {
  const emailsView = document.querySelector('#emails-view');
  const composeView = document.querySelector('#compose-view');

  // Show/hide
  emailsView.style.display = 'block';
  composeView.style.display = 'none';

  // Remove any existing detail views
  document.querySelectorAll('.detail-view').forEach(el => el.remove());

  // Header: capitalize the first character  
  emailsView.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch mailbox
  fetch(`/emails/${mailbox}`)
    .then(res => res.json())
    .then(emails => {
      if (!Array.isArray(emails)) {
        console.warn('Expected an array, got:', emails);
        return;
      }

      emails.forEach(email => {
        const row = document.createElement('div');
        row.className = 'email-row';
        row.style.border = '1px solid #ccc';
        row.style.padding = '10px';
        row.style.margin = '5px 0';
        row.style.background = email.read ? '#eee' : '#fff';
        row.style.cursor = 'pointer';
        row.innerHTML = `
          <strong>${mailbox === 'sent' ? email.recipients.join(', ') : email.sender}</strong>
          &nbsp;— ${email.subject}
          <span style="float:right;color:gray;">${email.timestamp}</span>
        `;
        row.addEventListener('click', () => {
          console.log('Opening email id:', email.id);
          view_email(email.id, mailbox);
        });
        emailsView.appendChild(row);
      });

      if (emails.length === 0) {
        const empty = document.createElement('div');
        empty.style.color = 'gray';
        empty.textContent = 'No emails here yet.';
        emailsView.appendChild(empty);
      }
    })
    .catch(err => console.error('Mailbox load failed:', err));
}


// View a single email
function view_email(id, mailbox) {
  fetch(`/emails/${id}`)
    .then(res => res.json())
    .then(email => {
      // Mark as read
      if (!email.read) {
        fetch(`/emails/${id}`, {
          method: 'PUT',
          body: JSON.stringify({ read: true })
        });
      }

      // Hide mailbox & compose
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#compose-view').style.display = 'none';

      // Remove old detail views
      document.querySelectorAll('.detail-view').forEach(el => el.remove());

      // Create detail container dynamically
      const detail = document.createElement('div');
      detail.className = 'detail-view';
      detail.style.padding = '15px';
      detail.style.border = '1px solid #ccc';
      detail.style.marginTop = '10px';
      detail.style.background = '#fafafa';

      // Info
      detail.innerHTML = `
        <p><strong>From:</strong> ${email.sender}</p>
        <p><strong>To:</strong> ${email.recipients.join(', ')}</p>
        <p><strong>Subject:</strong> ${email.subject}</p>
        <p><strong>Timestamp:</strong> ${email.timestamp}</p>
        <hr>
      `;

      // Buttons
      const btns = document.createElement('div');
      btns.style.marginBottom = '10px';

      if (mailbox !== 'sent') {
        const archiveBtn = document.createElement('button');
        archiveBtn.className = 'btn btn-sm btn-outline-primary';
        archiveBtn.textContent = email.archived ? 'Unarchive' : 'Archive';
        archiveBtn.onclick = () => {
          fetch(`/emails/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ archived: !email.archived })
          }).then(() => load_mailbox('inbox'));
        };
        btns.appendChild(archiveBtn);
      }

      const replyBtn = document.createElement('button');
      replyBtn.className = 'btn btn-sm btn-outline-success';
      replyBtn.style.marginLeft = '5px';
      replyBtn.textContent = 'Reply';
      replyBtn.onclick = () => {
        const subj = email.subject.startsWith('Re:') ? email.subject : `Re: ${email.subject}`;
        const body = `\n\nOn ${email.timestamp}, ${email.sender} wrote:\n${email.body}`;
        compose_email(email.sender, subj, body);
      };
      btns.appendChild(replyBtn);

      detail.appendChild(btns);

      // Body
      const bodyDiv = document.createElement('div');
      bodyDiv.style.whiteSpace = 'pre-wrap';
      bodyDiv.textContent = email.body;
      detail.appendChild(bodyDiv);

      // Add to DOM (after nav perhaps)
      document.body.appendChild(detail);
    })
    .catch(err => console.error('Email load failed:', err));
}
