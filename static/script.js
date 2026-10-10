let jobId = null;
let poll = null;

async function start() {
  const url = document.getElementById('url').value.trim();
  if (!url) {
    alert("Paste a playlist URL first.");
    return;
  }
  const container = document.querySelector('input[name="fmt"]:checked').value;

  document.getElementById('go').disabled = true;
  document.getElementById('status-panel').style.display = 'block';
  document.getElementById('log').innerText = 'initializing...';
  document.getElementById('bar').style.width = '0%';
  document.getElementById('percent').innerText = '0%';
  document.getElementById('dl').style.display = 'none';

  const res = await fetch('/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, container })
  });

  if (!res.ok) {
    document.getElementById('log').innerText = 'ERROR: could not start job';
    document.getElementById('go').disabled = false;
    return;
  }

  const data = await res.json();
  jobId = data.job_id;
  poll = setInterval(checkStatus, 1500);
}

async function checkStatus() {
  const res = await fetch('/status/' + jobId);
  const data = await res.json();

  document.getElementById('log').innerText = data.log.join('\n');
  document.getElementById('bar').style.width = data.percent + '%';
  document.getElementById('percent').innerText = data.percent + '%';

  if (data.state === 'done') {
    clearInterval(poll);
    document.getElementById('go').disabled = false;
    document.getElementById('bar').style.width = '100%';
    document.getElementById('percent').innerText = '100%';
    const dl = document.getElementById('dl');
    dl.href = '/download/' + jobId;
    dl.style.display = 'block';
  } else if (data.state === 'error') {
    clearInterval(poll);
    document.getElementById('go').disabled = false;
  }
}
