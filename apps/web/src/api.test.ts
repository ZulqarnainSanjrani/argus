import {describe,expect,it} from 'vitest';
import {isStale} from './api';

describe('API freshness',()=>{
  it('marks snapshots beyond their declared threshold stale',()=>{
    expect(isStale('2026-08-15T12:00:00Z',300,Date.parse('2026-08-15T12:06:00Z'))).toBe(true);
    expect(isStale('2026-08-15T12:00:00Z',300,Date.parse('2026-08-15T12:04:00Z'))).toBe(false);
  });
});
