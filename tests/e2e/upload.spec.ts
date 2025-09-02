import { test, expect } from '@playwright/test'
import path from 'path'

test.describe('File Upload Flow', () => {
  test('should display upload section on homepage', async ({ page }) => {
    await page.goto('/')
    
    await expect(page.getByText('Upload Your Data Files')).toBeVisible()
    await expect(page.getByText('Drop files here or click to browse')).toBeVisible()
    await expect(page.getByText('Supported formats: CSV, Excel, JSON, Parquet')).toBeVisible()
  })

  test('should show file format validation', async ({ page }) => {
    await page.goto('/')
    
    // Create a test file input
    const fileInput = page.locator('input[type="file"]')
    
    // Try to upload an unsupported file type
    const testFile = path.join(__dirname, '../fixtures/test.txt')
    await fileInput.setInputFiles(testFile)
    
    // Should show validation error
    await expect(page.getByText('Invalid file type')).toBeVisible()
  })

  test('should upload CSV file successfully', async ({ page }) => {
    await page.goto('/')
    
    const fileInput = page.locator('input[type="file"]')
    
    // Upload a CSV file
    const csvFile = path.join(__dirname, '../fixtures/sample.csv')
    await fileInput.setInputFiles(csvFile)
    
    // Should show upload progress
    await expect(page.getByText('Uploading')).toBeVisible()
    
    // Should show success message
    await expect(page.getByText('File uploaded successfully')).toBeVisible()
    
    // Should appear in uploaded files list
    await expect(page.getByText('sample.csv')).toBeVisible()
  })

  test('should display uploaded file metadata', async ({ page }) => {
    await page.goto('/')
    
    // Assuming a file is already uploaded
    await expect(page.getByText('Uploaded Files')).toBeVisible()
    
    // Should show file details
    await expect(page.locator('[data-testid="file-metadata"]')).toBeVisible()
    await expect(page.getByText(/\d+ rows, \d+ columns/)).toBeVisible()
    await expect(page.getByText(/\d+\.?\d* [KMGT]?B/)).toBeVisible()
  })
})