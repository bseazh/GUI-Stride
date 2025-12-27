
import { Merchant, LogEntry, ReportRecord } from './types';

export const MOCK_MERCHANTS: Merchant[] = [
  {
    id: '1',
    name: '考研法考资料',
    platform: '闲鱼',
    status: 'pirated',
    imageUrl: '2.png',
    uid: '9827214',
    reasoning: '该商家售价显著低于正版定价，且商品描述中包含“百度网盘秒发”、“PDF 电子版”等非法分发关键词。系统判定为：非授权分发。',
    evidenceImages: ['4.png', '5.png'],
    reportNumber: 'RP-20240522-001',
    reportDate: '2024-05-22 14:05'
  },
  {
    id: '2',
    name: '众合教育官方旗舰店',
    platform: '闲鱼',
    status: 'official',
    imageUrl: '1.png',
    uid: '9827215',
    reasoning: '官方正版渠道。', // 逻辑将在 App.tsx 中根据状态动态展示
    evidenceImages: ['6.png', '7.png']
  },
  {
    id: '3',
    name: '考公助手',
    platform: '闲鱼',
    status: 'pirated',
    imageUrl: '3.png',
    uid: '9827216',
    reasoning: '检测到该商品图片包含大量“电子版、视频赠送”等引流违规词，且价格极低。系统判定为：疑似盗版。',
    evidenceImages: ['8.png', '9.png'],
    reportNumber: 'RP-20240522-014',
    reportDate: '2024-05-22 15:30'
  }
];

export const INITIAL_LOGS: LogEntry[] = [
  {
    id: 'l1',
    timestamp: '14:20:01',
    type: 'info',
    message: '系统初始化完成，审计节点已接入...'
  }
];

export const MOCK_REPORTS: ReportRecord[] = [
  {
    id: 'r1',
    reportNumber: 'RP-20240522-001',
    merchantName: '阿强书屋',
    productName: '2024法考全套电子资料',
    price: 50,
    lossPrevented: 1200,
    reason: '非法网盘分发，包含加密水印关键词，确认为盗版。',
    date: '2024-05-22',
    screenshots: ['4.png']
  },
  {
    id: 'r2',
    reportNumber: 'RP-20240521-042',
    merchantName: '学霸笔记店',
    productName: '考研政治核心笔记',
    price: 15,
    lossPrevented: 850,
    reason: '扫描到非官方印制水印，低价倾销。',
    date: '2024-05-21',
    screenshots: ['8.png']
  }
];
