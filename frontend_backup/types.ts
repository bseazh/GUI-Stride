
export interface Merchant {
  id: string;
  name: string;
  platform: string;
  status: 'official' | 'pirated';
  imageUrl: string;
  uid: string;
  reasoning?: string;
  evidenceImages?: string[];
  reportNumber?: string;
  reportDate?: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  type: 'info' | 'performance' | 'action';
  message: string;
  metadata?: any;
}

export interface ReportRecord {
  id: string;
  reportNumber: string;
  merchantName: string;
  productName: string;
  price: number;
  lossPrevented: number;
  reason: string;
  date: string;
  screenshots: string[];
}

export interface WhitelistEntry {
  id: string;
  officialMerchantName: string;
  productName: string;
  price: string;
  allowedShops: string[];
}

export interface Device {
  id: string;
  name: string;
  status: 'online' | 'offline';
  isSelected: boolean;
}
