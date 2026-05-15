class WebSocketClient {
    constructor(jobId, onMessageCallback, onCompleteCallback, onErrorCallback) {
        this.jobId = jobId;
        this.url = `${WS_BASE}/progress/${jobId}`;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnect = 5;
        this.onMessage = onMessageCallback;
        this.onComplete = onCompleteCallback;
        this.onError = onErrorCallback;
    }

    connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log("WebSocket connected for job:", this.jobId);
            this.reconnectAttempts = 0;
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.onMessage(data);

                if (data.status === 'completed' || data.status === 'failed') {
                    this.onComplete(data);
                    this.ws.close();
                }
            } catch (e) {
                console.error("Failed to parse WS message", e);
            }
        };

        this.ws.onclose = (event) => {
            console.log("WebSocket closed.");
            // If not normally closed, try reconnecting
            if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnect) {
                this.reconnectAttempts++;
                setTimeout(() => this.connect(), 2000 * this.reconnectAttempts);
            }
        };

        this.ws.onerror = (error) => {
            console.error("WebSocket Error:", error);
            if (this.onError) this.onError(error);
        };
    }

    disconnect() {
        if (this.ws) {
            this.ws.close(1000, "User navigated away");
        }
    }
}
