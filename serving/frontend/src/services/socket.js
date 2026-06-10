import { io } from 'socket.io-client';

// ─── Cấu hình ──────────────────────────────────────────────────────────────
const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000';

/**
 * Khởi tạo kết nối WebSocket tới Backend Flask-SocketIO.
 * 
 * Events lắng nghe:
 *   - 'new_alert': Nhận alert mới khi có phát hiện xâm nhập
 *   - 'alert_status_updated': Nhận cập nhật khi alert được xử lý
 *   - 'connect': Kết nối thành công
 *   - 'disconnect': Mất kết nối
 */
const socketService = io(SOCKET_URL, {
  autoConnect: false,        // Không tự kết nối ngay khi import
  reconnection: true,        // Tự reconnect khi mất kết nối
  reconnectionAttempts: 10,  // Thử lại tối đa 10 lần
  reconnectionDelay: 2000,   // Chờ 2 giây giữa mỗi lần thử
  transports: ['websocket', 'polling'],  // Ưu tiên WebSocket, fallback polling
});

// ─── Event logging (chỉ trong development) ────────────────────────────────
if (process.env.NODE_ENV === 'development') {
  socketService.on('connect', () => {
    console.log('🟢 [WebSocket] Đã kết nối tới Backend:', SOCKET_URL);
  });

  socketService.on('disconnect', (reason) => {
    console.log('🔴 [WebSocket] Mất kết nối:', reason);
  });

  socketService.on('connect_error', (error) => {
    console.warn('⚠️ [WebSocket] Lỗi kết nối:', error.message);
  });

  socketService.on('reconnect', (attemptNumber) => {
    console.log(`🔄 [WebSocket] Đã reconnect thành công sau ${attemptNumber} lần thử.`);
  });
}

export default socketService;
