import { generateRandomAlert } from './mockData';

const USE_MOCK = true;

class MockSocket {
  constructor() {
    this.listeners = {};
    this.intervalId = null;
    this.connected = false;
  }

  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  }

  connect() {
    this.connected = true;
    this.emit('connect');
    
    // Giả lập nhận cảnh báo streaming mỗi 3-7 giây
    this.intervalId = setInterval(() => {
      const newAlert = generateRandomAlert();
      this.emit('new_alert', newAlert);
    }, Math.floor(Math.random() * 4000) + 3000); 
  }

  disconnect() {
    this.connected = false;
    this.emit('disconnect');
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }
}

// Nếu sau này kết nối backend thật, ta sẽ import { io } from 'socket.io-client' 
// và cấu hình io('http://localhost:5000') ở đây
const socketService = USE_MOCK ? new MockSocket() : null; // thay thế bằng io() khi dùng thật

export default socketService;
