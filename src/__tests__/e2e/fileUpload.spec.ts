/**
 * End-to-end tests for file upload functionality
 */

import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('File Upload E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('networkidle');
  });

  test('should display upload interface correctly', async ({ page }) => {
    // Check if upload section is visible
    await expect(page.getByText('Upload your data files')).toBeVisible();
    await expect(page.getByText('Drag and drop your CSV, Excel, JSON')).toBeVisible();
    await expect(page.getByText('Choose Files')).toBeVisible();
    await expect(page.getByText('Maximum file size: 500MB')).toBeVisible();
  });

  test('should upload a valid CSV file successfully', async ({ page }) => {
    // Create a temporary CSV file
    const csvContent = 'name,age,city\nJohn,30,New York\nJane,25,Los Angeles';
    const filePath = path.join(__dirname, 'temp-test.csv');
    
    // Use page.setInputFiles to upload
    const fileInput = page.locator('input[type="file"]');
    
    // Create a temporary file for testing
    await page.evaluate((content) => {
      const blob = new Blob([content], { type: 'text/csv' });
      const file = new File([blob], 'test.csv', { type: 'text/csv' });
      
      // Trigger file drop
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    }, csvContent);

    // Wait for file validation
    await expect(page.getByText('test.csv')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText('Valid')).toBeVisible({ timeout: 5000 });
  });

  test('should show validation errors for invalid files', async ({ page }) => {
    // Try to upload an invalid file type
    await page.evaluate(() => {
      const blob = new Blob(['malicious content'], { type: 'application/x-executable' });
      const file = new File([blob], 'malware.exe', { type: 'application/x-executable' });
      
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    // Should show validation error
    await expect(page.getByText('Invalid')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/File extension.*not allowed/)).toBeVisible();
  });

  test('should handle multiple file uploads', async ({ page }) => {
    // Upload multiple valid files
    await page.evaluate(() => {
      const file1 = new File(['name,age\nJohn,30'], 'file1.csv', { type: 'text/csv' });
      const file2 = new File(['{"name": "test"}'], 'file2.json', { type: 'application/json' });
      
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file1);
      event.dataTransfer?.items.add(file2);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    // Check both files appear
    await expect(page.getByText('file1.csv')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText('file2.json')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText('Uploaded Files (2)')).toBeVisible();
  });

  test('should allow file removal', async ({ page }) => {
    // Upload a file first
    await page.evaluate(() => {
      const file = new File(['name,age\nJohn,30'], 'test.csv', { type: 'text/csv' });
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    // Wait for file to appear
    await expect(page.getByText('test.csv')).toBeVisible({ timeout: 5000 });

    // Click remove button
    await page.getByRole('button', { name: /remove/i }).first().click();

    // File should be removed
    await expect(page.getByText('test.csv')).not.toBeVisible();
  });

  test('should show upload progress and complete successfully', async ({ page }) => {
    // Upload a valid file
    await page.evaluate(() => {
      const file = new File(['name,age\nJohn,30'], 'test.csv', { type: 'text/csv' });
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    // Wait for validation
    await expect(page.getByText('Upload Valid Files (1)')).toBeVisible({ timeout: 5000 });

    // Click upload button
    await page.getByText('Upload Valid Files (1)').click();

    // Should show uploading state
    await expect(page.getByText('Uploading')).toBeVisible({ timeout: 2000 });

    // Should eventually show uploaded state
    await expect(page.getByText('Uploaded')).toBeVisible({ timeout: 10000 });
  });

  test('should switch to chat tab after successful upload', async ({ page }) => {
    // Start on upload tab
    await expect(page.getByRole('tab', { name: 'Upload' })).toHaveAttribute('aria-selected', 'true');

    // Upload a valid file
    await page.evaluate(() => {
      const file = new File(['name,age\nJohn,30'], 'test.csv', { type: 'text/csv' });
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    // Wait for file validation and tab switch
    await expect(page.getByText('Chat')).toBeVisible({ timeout: 5000 });
    
    // Chat tab should become active
    await expect(page.getByRole('tab', { name: 'Chat' })).not.toHaveAttribute('aria-disabled');
  });

  test('should disable tabs when no files are uploaded', async ({ page }) => {
    // Initially, chat, preview, and files tabs should be disabled
    await expect(page.getByRole('tab', { name: 'Chat' })).toHaveAttribute('aria-disabled');
    await expect(page.getByRole('tab', { name: 'Preview' })).toHaveAttribute('aria-disabled');
    await expect(page.getByRole('tab', { name: /Files/ })).toHaveAttribute('aria-disabled');
  });

  test('should handle large file warnings', async ({ page }) => {
    // Create a large file (simulated)
    await page.evaluate(() => {
      const largeContent = 'a'.repeat(100 * 1024 * 1024); // 100MB
      const file = new File([largeContent], 'large.csv', { type: 'text/csv' });
      
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    // Should show warning for large file
    await expect(page.getByText(/Large file detected/)).toBeVisible({ timeout: 5000 });
  });

  test('should respect max files limit', async ({ page }) => {
    // Upload more than 10 files to test the limit
    await page.evaluate(() => {
      const dt = new DataTransfer();
      
      // Add 12 files (over the 10 file limit)
      for (let i = 1; i <= 12; i++) {
        const file = new File([`data${i}`], `file${i}.csv`, { type: 'text/csv' });
        dt.items.add(file);
      }
      
      const event = new DragEvent('drop', { dataTransfer: dt });
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    // Should only show 10 files
    await page.waitForTimeout(2000); // Wait for processing
    const fileElements = await page.locator('[data-testid="uploaded-file"]').count();
    expect(fileElements).toBeLessThanOrEqual(10);
  });

  test('should show appropriate error messages for server errors', async ({ page }) => {
    // Mock a server error by intercepting the upload request
    await page.route('**/api/v1/files/upload', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      });
    });

    // Upload a file
    await page.evaluate(() => {
      const file = new File(['name,age\nJohn,30'], 'test.csv', { type: 'text/csv' });
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    // Wait for validation and upload
    await expect(page.getByText('Upload Valid Files (1)')).toBeVisible({ timeout: 5000 });
    await page.getByText('Upload Valid Files (1)').click();

    // Should show error message
    await expect(page.getByText(/Server error during upload/)).toBeVisible({ timeout: 5000 });
  });
});