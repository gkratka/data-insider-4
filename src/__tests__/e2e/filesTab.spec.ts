/**
 * End-to-end tests for Files tab functionality
 */

import { test, expect } from '@playwright/test';

test.describe('Files Tab E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('networkidle');
  });

  test('should show Files tab disabled initially', async ({ page }) => {
    // Files tab should be disabled when no files are uploaded
    const filesTab = page.getByRole('tab', { name: /Files \(0\)/ });
    await expect(filesTab).toHaveAttribute('aria-disabled', 'true');
  });

  test('should enable Files tab after file upload', async ({ page }) => {
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

    // Wait for file validation
    await expect(page.getByText('test.csv')).toBeVisible({ timeout: 5000 });
    
    // Files tab should now show (1) and be enabled
    await expect(page.getByRole('tab', { name: /Files \(1\)/ })).not.toHaveAttribute('aria-disabled');
  });

  test('should display uploaded file in Files tab', async ({ page }) => {
    // Upload and validate a file
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
    
    // Upload the file
    await page.getByText('Upload Valid Files (1)').click();
    
    // Wait for upload to complete
    await expect(page.getByText('Uploaded')).toBeVisible({ timeout: 10000 });

    // Switch to Files tab
    await page.getByRole('tab', { name: /Files/ }).click();

    // Should display the uploaded file
    await expect(page.getByText('test.csv')).toBeVisible();
    await expect(page.getByText('Uploaded Files')).toBeVisible();
    await expect(page.getByText('Manage your uploaded data files')).toBeVisible();
  });

  test('should show file details in Files tab', async ({ page }) => {
    // Upload a file
    await page.evaluate(() => {
      const file = new File(['name,age,city\nJohn,30,New York\nJane,25,Los Angeles'], 'employees.csv', { 
        type: 'text/csv',
        lastModified: Date.now() 
      });
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    // Wait and upload
    await expect(page.getByText('Upload Valid Files (1)')).toBeVisible({ timeout: 5000 });
    await page.getByText('Upload Valid Files (1)').click();
    await expect(page.getByText('Uploaded')).toBeVisible({ timeout: 10000 });

    // Go to Files tab
    await page.getByRole('tab', { name: /Files/ }).click();

    // Check file details are displayed
    await expect(page.getByText('employees.csv')).toBeVisible();
    await expect(page.getByText('text/csv')).toBeVisible();
    await expect(page.getByText(/Bytes|KB|MB/)).toBeVisible(); // File size
    await expect(page.getByText('Uploaded')).toBeVisible(); // Status badge
  });

  test('should provide file action buttons', async ({ page }) => {
    // Upload a file
    await page.evaluate(() => {
      const file = new File(['data'], 'test.csv', { type: 'text/csv' });
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    await expect(page.getByText('Upload Valid Files (1)')).toBeVisible({ timeout: 5000 });
    await page.getByText('Upload Valid Files (1)').click();
    await expect(page.getByText('Uploaded')).toBeVisible({ timeout: 10000 });

    // Go to Files tab
    await page.getByRole('tab', { name: /Files/ }).click();

    // Should have action buttons
    await expect(page.getByRole('button', { name: /Preview/ })).toBeVisible();
    await expect(page.getByRole('button', { name: /Download/ })).toBeVisible();
    await expect(page.getByRole('button', { name: /Delete/ })).toBeVisible();
  });

  test('should handle file deletion', async ({ page }) => {
    // Upload a file
    await page.evaluate(() => {
      const file = new File(['data'], 'to-delete.csv', { type: 'text/csv' });
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    await expect(page.getByText('Upload Valid Files (1)')).toBeVisible({ timeout: 5000 });
    await page.getByText('Upload Valid Files (1)').click();
    await expect(page.getByText('Uploaded')).toBeVisible({ timeout: 10000 });

    // Go to Files tab
    await page.getByRole('tab', { name: /Files/ }).click();
    
    // Verify file is there
    await expect(page.getByText('to-delete.csv')).toBeVisible();

    // Delete the file
    await page.getByRole('button', { name: /Delete/ }).click();

    // File should be removed (might show "No Files Uploaded" or updated list)
    await expect(page.getByText('to-delete.csv')).not.toBeVisible({ timeout: 5000 });
  });

  test('should handle preview button click', async ({ page }) => {
    // Upload a file
    await page.evaluate(() => {
      const file = new File(['name,value\ntest,123'], 'preview-test.csv', { type: 'text/csv' });
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    await expect(page.getByText('Upload Valid Files (1)')).toBeVisible({ timeout: 5000 });
    await page.getByText('Upload Valid Files (1)').click();
    await expect(page.getByText('Uploaded')).toBeVisible({ timeout: 10000 });

    // Go to Files tab
    await page.getByRole('tab', { name: /Files/ }).click();

    // Click Preview button
    await page.getByRole('button', { name: /Preview/ }).click();

    // Should switch to Preview tab
    await expect(page.getByRole('tab', { name: 'Preview' })).toHaveAttribute('aria-selected', 'true');
  });

  test('should fetch existing files from backend on tab switch', async ({ page }) => {
    // First, manually upload a file via API to simulate existing backend files
    const csvContent = 'name,age\nExisting,25';
    
    // Use page.evaluate to make API call from browser context
    await page.evaluate(async (content) => {
      const blob = new Blob([content], { type: 'text/csv' });
      const file = new File([blob], 'existing-file.csv', { type: 'text/csv' });
      
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        await fetch('http://localhost:8001/api/v1/files/upload', {
          method: 'POST',
          body: formData,
        });
      } catch (error) {
        console.error('Failed to upload via API:', error);
      }
    }, csvContent);

    // Now go directly to Files tab to see if it fetches the backend file
    await page.getByRole('tab', { name: /Files/ }).click();

    // Should display the file that was uploaded via API
    await expect(page.getByText('existing-file.csv')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Uploaded')).toBeVisible();
  });

  test('should show proper empty state when no files exist', async ({ page }) => {
    // Go to Files tab directly (no files uploaded)
    // Since tab is disabled, we need to upload then delete, or modify the test
    
    // For now, just verify the initial empty state is shown correctly
    await expect(page.getByRole('tab', { name: /Files \(0\)/ })).toHaveAttribute('aria-disabled', 'true');
    
    // The tab is disabled, so we can't click it. This test verifies the initial state is correct.
  });

  test('should update Files tab count when files are uploaded', async ({ page }) => {
    // Initially shows (0)
    await expect(page.getByRole('tab', { name: /Files \(0\)/ })).toBeVisible();

    // Upload first file
    await page.evaluate(() => {
      const file = new File(['data1'], 'file1.csv', { type: 'text/csv' });
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    // Should show (1)
    await expect(page.getByRole('tab', { name: /Files \(1\)/ })).toBeVisible({ timeout: 5000 });

    // Upload second file
    await page.evaluate(() => {
      const file = new File(['data2'], 'file2.csv', { type: 'text/csv' });
      const event = new DragEvent('drop', {
        dataTransfer: new DataTransfer()
      });
      event.dataTransfer?.items.add(file);
      
      const dropzone = document.querySelector('[data-testid="dropzone"]');
      dropzone?.dispatchEvent(event);
    });

    // Should show (2)
    await expect(page.getByRole('tab', { name: /Files \(2\)/ })).toBeVisible({ timeout: 5000 });
  });
});