/**
 * Secure file validation service for data intelligence platform
 * Implements comprehensive security checks for file uploads
 */

export interface FileValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  fileInfo?: {
    name: string;
    size: number;
    type: string;
    extension: string;
  };
}

export interface FileValidationConfig {
  maxFileSize: number; // in bytes
  allowedTypes: string[];
  allowedExtensions: string[];
  maxFilenameLength: number;
  scanForMalware?: boolean;
}

// Default secure configuration
const DEFAULT_CONFIG: FileValidationConfig = {
  maxFileSize: 500 * 1024 * 1024, // 500MB
  allowedTypes: [
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/json',
    'text/plain',
    'application/vnd.apache.parquet'
  ],
  allowedExtensions: ['.csv', '.xlsx', '.xls', '.json', '.txt', '.parquet'],
  maxFilenameLength: 255,
  scanForMalware: true
};

class FileValidationService {
  private config: FileValidationConfig;

  constructor(config?: Partial<FileValidationConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Validate a single file with comprehensive security checks
   */
  async validateFile(file: File): Promise<FileValidationResult> {
    const errors: string[] = [];
    const warnings: string[] = [];

    try {
      // Extract file information
      const fileInfo = {
        name: file.name,
        size: file.size,
        type: file.type,
        extension: this.getFileExtension(file.name)
      };

      // 1. Filename validation
      if (!this.isValidFilename(file.name)) {
        errors.push('Invalid filename. Only alphanumeric characters, hyphens, underscores, and dots are allowed.');
      }

      if (file.name.length > this.config.maxFilenameLength) {
        errors.push(`Filename too long. Maximum ${this.config.maxFilenameLength} characters allowed.`);
      }

      // 2. File size validation
      if (file.size === 0) {
        errors.push('File is empty.');
      }

      if (file.size > this.config.maxFileSize) {
        errors.push(`File size exceeds limit. Maximum ${this.formatBytes(this.config.maxFileSize)} allowed.`);
      }

      // 3. File type validation
      if (!this.isAllowedType(file.type)) {
        errors.push(`File type '${file.type}' is not allowed. Allowed types: ${this.config.allowedTypes.join(', ')}`);
      }

      // 4. File extension validation
      if (!this.isAllowedExtension(fileInfo.extension)) {
        errors.push(`File extension '${fileInfo.extension}' is not allowed. Allowed extensions: ${this.config.allowedExtensions.join(', ')}`);
      }

      // 5. MIME type vs extension consistency check
      if (!this.isMimeTypeConsistent(file.type, fileInfo.extension)) {
        warnings.push('File extension and MIME type may not match. This could indicate a renamed file.');
      }

      // 6. Content validation (read first few bytes)
      const contentValidation = await this.validateFileContent(file);
      if (!contentValidation.isValid) {
        errors.push(...contentValidation.errors);
      }

      // 7. Check for potentially dangerous content
      const securityCheck = await this.performSecurityCheck(file);
      if (!securityCheck.isValid) {
        errors.push(...securityCheck.errors);
        warnings.push(...securityCheck.warnings);
      }

      return {
        isValid: errors.length === 0,
        errors,
        warnings,
        fileInfo
      };

    } catch (error) {
      return {
        isValid: false,
        errors: [`Validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
        warnings: []
      };
    }
  }

  /**
   * Validate multiple files
   */
  async validateFiles(files: File[]): Promise<FileValidationResult[]> {
    const results = await Promise.all(
      files.map(file => this.validateFile(file))
    );

    return results;
  }

  /**
   * Check if filename contains only safe characters
   */
  private isValidFilename(filename: string): boolean {
    // Allow alphanumeric, hyphens, underscores, dots, and spaces
    const validPattern = /^[a-zA-Z0-9.\-_ ]+$/;
    return validPattern.test(filename) && !filename.startsWith('.') && !filename.endsWith('.');
  }

  /**
   * Extract file extension safely
   */
  private getFileExtension(filename: string): string {
    const lastDot = filename.lastIndexOf('.');
    return lastDot !== -1 ? filename.slice(lastDot).toLowerCase() : '';
  }

  /**
   * Check if file type is allowed
   */
  private isAllowedType(mimeType: string): boolean {
    return this.config.allowedTypes.includes(mimeType);
  }

  /**
   * Check if file extension is allowed
   */
  private isAllowedExtension(extension: string): boolean {
    return this.config.allowedExtensions.includes(extension);
  }

  /**
   * Check consistency between MIME type and file extension
   */
  private isMimeTypeConsistent(mimeType: string, extension: string): boolean {
    const mimeExtensionMap: Record<string, string[]> = {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json'],
      'text/plain': ['.txt', '.csv'],
      'application/vnd.apache.parquet': ['.parquet']
    };

    const expectedExtensions = mimeExtensionMap[mimeType];
    return expectedExtensions ? expectedExtensions.includes(extension) : true;
  }

  /**
   * Validate file content by reading headers
   */
  private async validateFileContent(file: File): Promise<{ isValid: boolean; errors: string[] }> {
    try {
      // Read first 512 bytes to check file headers
      const headerBuffer = await this.readFileHeader(file, 512);
      const headerBytes = new Uint8Array(headerBuffer);

      // Check for common file signatures
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        return this.validateCSVContent(headerBytes);
      }

      if (file.type.includes('excel') || file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        return this.validateExcelContent(headerBytes);
      }

      if (file.type === 'application/json' || file.name.endsWith('.json')) {
        return this.validateJSONContent(headerBytes);
      }

      return { isValid: true, errors: [] };
    } catch (error) {
      return {
        isValid: false,
        errors: [`Content validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`]
      };
    }
  }

  /**
   * Read file header bytes
   */
  private readFileHeader(file: File, bytes: number): Promise<ArrayBuffer> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as ArrayBuffer);
      reader.onerror = () => reject(reader.error);
      reader.readAsArrayBuffer(file.slice(0, bytes));
    });
  }

  /**
   * Validate CSV file content
   */
  private validateCSVContent(headerBytes: Uint8Array): { isValid: boolean; errors: string[] } {
    try {
      const headerText = new TextDecoder('utf-8').decode(headerBytes);
      
      // Check for common CSV patterns
      const hasCommas = headerText.includes(',');
      const hasSemicolons = headerText.includes(';');
      const hasNewlines = headerText.includes('\n') || headerText.includes('\r');

      if (!hasCommas && !hasSemicolons) {
        return { isValid: false, errors: ['File does not appear to be a valid CSV format'] };
      }

      // Check for potentially malicious content
      if (headerText.includes('<script') || headerText.includes('<?php')) {
        return { isValid: false, errors: ['File contains potentially malicious content'] };
      }

      return { isValid: true, errors: [] };
    } catch (error) {
      return { isValid: false, errors: ['Unable to validate CSV content'] };
    }
  }

  /**
   * Validate Excel file content
   */
  private validateExcelContent(headerBytes: Uint8Array): { isValid: boolean; errors: string[] } {
    // Check for Excel file signatures
    const xlsxSignature = [0x50, 0x4B, 0x03, 0x04]; // ZIP signature (XLSX)
    const xlsSignature = [0xD0, 0xCF, 0x11, 0xE0]; // OLE signature (XLS)

    const hasXlsxSignature = this.bytesMatch(headerBytes, xlsxSignature);
    const hasXlsSignature = this.bytesMatch(headerBytes, xlsSignature);

    if (!hasXlsxSignature && !hasXlsSignature) {
      return { isValid: false, errors: ['File does not appear to be a valid Excel format'] };
    }

    return { isValid: true, errors: [] };
  }

  /**
   * Validate JSON file content
   */
  private validateJSONContent(headerBytes: Uint8Array): { isValid: boolean; errors: string[] } {
    try {
      const headerText = new TextDecoder('utf-8').decode(headerBytes);
      const trimmed = headerText.trim();

      // Check if it starts with valid JSON characters
      if (!trimmed.startsWith('{') && !trimmed.startsWith('[')) {
        return { isValid: false, errors: ['File does not appear to be valid JSON format'] };
      }

      // Try to parse a portion to validate JSON structure
      try {
        JSON.parse(trimmed);
      } catch {
        // If partial parse fails, it might be a large file - just check structure
        const hasValidStructure = /^[\s]*[{\[]/.test(trimmed);
        if (!hasValidStructure) {
          return { isValid: false, errors: ['Invalid JSON structure'] };
        }
      }

      return { isValid: true, errors: [] };
    } catch (error) {
      return { isValid: false, errors: ['Unable to validate JSON content'] };
    }
  }

  /**
   * Check if bytes match a signature
   */
  private bytesMatch(buffer: Uint8Array, signature: number[]): boolean {
    for (let i = 0; i < signature.length; i++) {
      if (buffer[i] !== signature[i]) {
        return false;
      }
    }
    return true;
  }

  /**
   * Perform additional security checks
   */
  private async performSecurityCheck(file: File): Promise<{ isValid: boolean; errors: string[]; warnings: string[] }> {
    const errors: string[] = [];
    const warnings: string[] = [];

    try {
      // Check for suspicious patterns in filename
      const suspiciousPatterns = [
        /\.(exe|bat|cmd|scr|pif|com|jar)$/i,
        /\.(php|asp|jsp|html|htm)$/i,
        /\.(sh|bash|ps1|vbs)$/i
      ];

      for (const pattern of suspiciousPatterns) {
        if (pattern.test(file.name)) {
          errors.push('File type is potentially dangerous and not allowed');
          break;
        }
      }

      // Check for double extensions
      if ((file.name.match(/\./g) || []).length > 1) {
        const parts = file.name.split('.');
        if (parts.length > 2) {
          warnings.push('File has multiple extensions. Verify this is intentional.');
        }
      }

      // Check file size patterns (unusually large or small files)
      if (file.size > 100 * 1024 * 1024) { // 100MB
        warnings.push('Large file detected. Processing may take longer.');
      }

      return { isValid: errors.length === 0, errors, warnings };
    } catch (error) {
      return {
        isValid: false,
        errors: [`Security check failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
        warnings: []
      };
    }
  }

  /**
   * Format bytes to human readable string
   */
  private formatBytes(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Update validation configuration
   */
  updateConfig(newConfig: Partial<FileValidationConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * Get current configuration
   */
  getConfig(): FileValidationConfig {
    return { ...this.config };
  }
}

// Export singleton instance
export const fileValidationService = new FileValidationService();
export { FileValidationService };