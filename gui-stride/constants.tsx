
import { Merchant, LogEntry, ReportRecord } from './types';

export const MOCK_MERCHANTS: Merchant[] = [
  {
    id: '1',
    name: '24届法考资料专营',
    platform: '闲鱼',
    status: 'pirated',
    imageUrl: 'https://picsum.photos/seed/m1/200/200',
    uid: '9827214',
    reasoning: '该商家售价显著低于正版定价（¥299 vs ¥50），且商品描述中包含“百度网盘秒发”、“电子版”等非法分发关键词。店铺资质为个人，无出版社授权证明。',
    evidenceImages: ['https://picsum.photos/seed/ev1/400/800', 'https://picsum.photos/seed/ev2/400/800'],
    reportNumber: 'RP-20240522-001',
    reportDate: '2024-05-22 14:05'
  },
  {
    id: '2',
    name: '官方图书旗舰店',
    platform: '闲鱼',
    status: 'official',
    imageUrl: 'https://picsum.photos/seed/m2/200/200',
    uid: '9827215'
  },
  {
    id: '3',
    name: '考研学长资料室',
    platform: '闲鱼',
    status: 'pirated',
    imageUrl: 'https://picsum.photos/seed/m3/200/200',
    uid: '9827216',
    reasoning: '检测到该商品图片包含其他平台水印，卖家在回复中引导至私域交易（微信），符合典型盗版引流特征。',
    evidenceImages: ['https://picsum.photos/seed/ev3/400/800'],
    reportNumber: 'RP-20240522-014',
    reportDate: '2024-05-22 15:30'
  }
];

export const INITIAL_LOGS: LogEntry[] = [
  {
    id: 'l1',
    timestamp: '14:20:01',
    type: 'info',
    message: '系统初始化完成，等待指令...'
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
    screenshots: ['https://picsum.photos/seed/scr1/200/200']
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
    screenshots: ['https://picsum.photos/seed/scr2/200/200']
  },
  {
    id: 'r3',
    reportNumber: 'RP-20240520-112',
    merchantName: '考公助手',
    productName: '国考历年真题解析集',
    price: 35,
    lossPrevented: 2400,
    reason: '私域引流，证据链显示卖家引导微信转账。',
    date: '2024-05-20',
    screenshots: ['https://picsum.photos/seed/scr3/200/200']
  }
];
