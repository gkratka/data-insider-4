/**
 * Tests for file validation service
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { fileValidationService, FileValidationService } from '../services/fileValidationService';

// Mock File constructor for testing
class MockFile extends File {
  constructor(bits: BlobPart[], filename: string, options?: FilePropertyBag) {
    super(bits, filename, options);
  }
}

describe('FileValidationService', () => {
  let service: FileValidationService;

  beforeEach(() => {
    service = new FileValidationService();
  });

  describe('validateFile', () => {
    it('should validate a valid CSV file', async () => {
      const csvContent = 'name,age,city\nJohn,30,New York\nJane,25,Los Angeles';
      const file = new MockFile([csvContent], 'test.csv', { type: 'text/csv' });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.fileInfo?.name).toBe('test.csv');
      expect(result.fileInfo?.extension).toBe('.csv');
    });

    it('should validate a valid Excel file', async () => {
      // Mock Excel file signature (ZIP header for XLSX)
      const xlsxHeader = new Uint8Array([0x50, 0x4B, 0x03, 0x04]);
      const file = new MockFile([xlsxHeader], 'test.xlsx', { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.fileInfo?.extension).toBe('.xlsx');
    });

    it('should validate a valid JSON file', async () => {
      const jsonContent = '{"name": "test", "data": [1, 2, 3]}';
      const file = new MockFile([jsonContent], 'test.json', { type: 'application/json' });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.fileInfo?.extension).toBe('.json');
    });

    it('should reject files with invalid extensions', async () => {
      const file = new MockFile(['test content'], 'test.exe', { type: 'application/octet-stream' });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(expect.stringContaining('File extension \'.exe\' is not allowed'));
    });

    it('should reject files that are too large', async () => {
      const service = new FileValidationService({ maxFileSize: 1024 }); // 1KB limit
      const largeContent = 'a'.repeat(2048); // 2KB content
      const file = new MockFile([largeContent], 'large.csv', { type: 'text/csv' });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(expect.stringContaining('File size exceeds limit'));
    });

    it('should reject empty files', async () => {
      const file = new MockFile([''], 'empty.csv', { type: 'text/csv' });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('File is empty.');
    });

    it('should reject files with invalid filenames', async () => {
      const file = new MockFile(['test'], 'file<>name.csv', { type: 'text/csv' });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(expect.stringContaining('Invalid filename'));
    });

    it('should reject files with disallowed MIME types', async () => {
      const file = new MockFile(['test'], 'test.csv', { type: 'application/x-malware' });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(expect.stringContaining('File type \'application/x-malware\' is not allowed'));
    });

    it('should warn about MIME type and extension mismatch', async () => {
      const file = new MockFile(['test'], 'test.csv', { type: 'application/json' });

      const result = await service.validateFile(file);

      expect(result.warnings).toContain(expect.stringContaining('File extension and MIME type may not match'));
    });

    it('should detect potentially dangerous files', async () => {
      const file = new MockFile(['test'], 'malware.exe.csv', { type: 'text/csv' });

      const result = await service.validateFile(file);

      expect(result.warnings).toContain(expect.stringContaining('multiple extensions'));
    });

    it('should reject CSV files without proper separators', async () => {
      const invalidCsv = 'This is not a CSV file just plain text';
      const file = new MockFile([invalidCsv], 'invalid.csv', { type: 'text/csv' });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(expect.stringContaining('does not appear to be a valid CSV format'));
    });

    it('should detect malicious content in CSV', async () => {
      const maliciousCsv = 'name,code\nJohn,<script>alert("hack")</script>';
      const file = new MockFile([maliciousCsv], 'malicious.csv', { type: 'text/csv' });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(expect.stringContaining('potentially malicious content'));
    });

    it('should validate proper JSON structure', async () => {
      const invalidJson = 'This is not JSON';
      const file = new MockFile([invalidJson], 'invalid.json', { type: 'application/json' });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(expect.stringContaining('does not appear to be valid JSON format'));
    });
  });

  describe('validateFiles', () => {
    it('should validate multiple files', async () => {
      const file1 = new MockFile(['name,age\nJohn,30'], 'test1.csv', { type: 'text/csv' });
      const file2 = new MockFile(['{"test": true}'], 'test2.json', { type: 'application/json' });
      const file3 = new MockFile(['invalid'], 'test.exe', { type: 'application/octet-stream' });

      const results = await service.validateFiles([file1, file2, file3]);

      expect(results).toHaveLength(3);
      expect(results[0].isValid).toBe(true);
      expect(results[1].isValid).toBe(true);
      expect(results[2].isValid).toBe(false);
    });
  });

  describe('configuration', () => {
    it('should allow custom configuration', () => {
      const customConfig = {
        maxFileSize: 1024,
        allowedTypes: ['text/plain'],
        allowedExtensions: ['.txt'],
        maxFilenameLength: 50
      };

      const customService = new FileValidationService(customConfig);
      const config = customService.getConfig();

      expect(config.maxFileSize).toBe(1024);
      expect(config.allowedTypes).toEqual(['text/plain']);
      expect(config.allowedExtensions).toEqual(['.txt']);
      expect(config.maxFilenameLength).toBe(50);
    });

    it('should allow configuration updates', () => {
      service.updateConfig({ maxFileSize: 2048 });
      const config = service.getConfig();

      expect(config.maxFileSize).toBe(2048);
    });
  });

  describe('edge cases', () => {
    it('should handle files without extensions', async () => {
      const file = new MockFile(['test'], 'noextension', { type: 'text/plain' });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(expect.stringContaining('File extension \'\' is not allowed'));
    });

    it('should handle very long filenames', async () => {
      const longName = 'a'.repeat(300) + '.csv';
      const file = new MockFile(['test'], longName, { type: 'text/csv' });

      const result = await service.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(expect.stringContaining('Filename too long'));
    });

    it('should handle files with no MIME type', async () => {
      const file = new MockFile(['name,age\nJohn,30'], 'test.csv', { type: '' });

      const result = await service.validateFile(file);

      // Should still validate based on extension
      expect(result.fileInfo?.type).toBe('');
    });
  });
});