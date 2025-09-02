import { test, expect, Page } from '@playwright/test';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

/**
 * Integration tests for file upload and chat functionality
 * Testing the file ID mapping fix identified in FRONTEND_INTEGRATION_TEST_REPORT.md
 */

// ES module __dirname equivalent
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create test CSV file
const createTestCSV = () => {
  const testData = `name,age,salary,department,region
John,25,50000,Engineering,North
Alice,30,75000,Engineering,South
Bob,35,60000,Sales,North
Charlie,28,55000,Marketing,East
David,40,80000,Sales,West`;
  
  const testFilePath = path.join(__dirname, 'test-data.csv');
  fs.writeFileSync(testFilePath, testData);
  return testFilePath;
};

test.describe('File Upload and Chat Integration', () => {
  let page: Page;
  let testFilePath: string;

  test.beforeAll(async ({ browser }) => {
    page = await browser.newPage();
    testFilePath = createTestCSV();
    
    // Ensure backend is running
    await page.goto('http://localhost:8000/health', { waitUntil: 'networkidle' });
    await expect(page.getByText('healthy')).toBeVisible();
  });

  test.afterAll(async () => {
    // Clean up test file
    if (fs.existsSync(testFilePath)) {
      fs.unlinkSync(testFilePath);
    }
    await page.close();
  });

  test.beforeEach(async () => {
    // Start fresh for each test
    await page.goto('http://localhost:8081', { waitUntil: 'networkidle' });
  });

  test('should upload file and receive correct file ID from backend', async () => {
    // Navigate to upload tab
    await page.getByRole('tab', { name: 'Upload' }).click();
    
    // Upload the test file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testFilePath);
    
    // Wait for upload to complete
    await expect(page.getByText('Complete')).toBeVisible({ timeout: 10000 });
    
    // Verify file appears in upload section with correct name
    await expect(page.getByText('test-data.csv')).toBeVisible();
  });

  test('should automatically switch to chat tab after file upload', async () => {
    // Start in upload tab
    await page.getByRole('tab', { name: 'Upload' }).click();
    
    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testFilePath);
    
    // Wait for upload and auto-switch to chat
    await expect(page.getByText('Complete')).toBeVisible({ timeout: 10000 });
    
    // Should auto-switch to chat tab
    await expect(page.getByRole('tab', { name: 'Chat' })).toHaveAttribute('data-state', 'active');
  });

  test('should display uploaded file in chat context', async () => {
    // Upload file first
    await page.getByRole('tab', { name: 'Upload' }).click();
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testFilePath);
    await expect(page.getByText('Complete')).toBeVisible({ timeout: 10000 });
    
    // Go to chat tab
    await page.getByRole('tab', { name: 'Chat' }).click();
    
    // Verify file appears in context section
    await expect(page.getByText('Context Files')).toBeVisible();
    await expect(page.getByText('test-data.csv')).toBeVisible();
  });

  test('should successfully send chat message and receive response', async () => {
    // Upload file first
    await page.getByRole('tab', { name: 'Upload' }).click();
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testFilePath);
    await expect(page.getByText('Complete')).toBeVisible({ timeout: 10000 });
    
    // Navigate to chat
    await page.getByRole('tab', { name: 'Chat' }).click();
    
    // Send a test message
    const chatInput = page.getByPlaceholder('Ask a question about your data...');
    await chatInput.fill('what can you tell me about the data that was uploaded?');
    
    const sendButton = page.getByRole('button', { name: 'Send' });
    await sendButton.click();
    
    // Wait for response (should NOT contain "File not found")
    await expect(page.getByText('AI is thinking...')).toBeVisible();
    
    // Wait for actual response - should contain data information, not file not found error
    const responseLocator = page.locator('[class*="bg-muted"]:has-text("Result")');
    await expect(responseLocator).toBeVisible({ timeout: 15000 });
    
    // Verify we don't get the file not found error
    await expect(page.getByText('File \'file-')).not.toBeVisible();
    await expect(page.getByText('not found')).not.toBeVisible();
  });

  test('should handle complex LLM queries correctly', async () => {
    // Upload file first
    await page.getByRole('tab', { name: 'Upload' }).click();
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testFilePath);
    await expect(page.getByText('Complete')).toBeVisible({ timeout: 10000 });
    
    // Navigate to chat
    await page.getByRole('tab', { name: 'Chat' }).click();
    
    // Test Phase 3 LLM code generation with complex query
    const chatInput = page.getByPlaceholder('Ask a question about your data...');
    await chatInput.fill('calculate the average salary by department');
    
    const sendButton = page.getByRole('button', { name: 'Send' });
    await sendButton.click();
    
    // Wait for response
    await expect(page.getByText('AI is thinking...')).toBeVisible();
    
    // Should get generated code response
    const codeResponse = page.locator(':text("Generated Code:")');
    await expect(codeResponse).toBeVisible({ timeout: 15000 });
    
    // Verify we get actual results, not file not found
    await expect(page.getByText('File \'file-')).not.toBeVisible();
    await expect(page.getByText('not found')).not.toBeVisible();
  });

  test('should display file information in Files tab', async () => {
    // Upload file first
    await page.getByRole('tab', { name: 'Upload' }).click();
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testFilePath);
    await expect(page.getByText('Complete')).toBeVisible({ timeout: 10000 });
    
    // Navigate to Files tab
    await page.getByRole('tab', { name: /Files \(\d+\)/ }).click();
    
    // Should show file information
    await expect(page.getByText('test-data.csv')).toBeVisible();
    
    // Should be able to delete file
    const deleteButton = page.getByRole('button', { name: 'Delete' }).first();
    await deleteButton.click();
    
    // Confirm deletion if modal appears
    const confirmButton = page.getByRole('button', { name: 'Delete', exact: true });
    if (await confirmButton.isVisible()) {
      await confirmButton.click();
    }
  });

  test('should handle multiple file uploads correctly', async () => {
    // Create second test file
    const testData2 = `product,price,category
Widget,10.99,Electronics
Gadget,25.50,Electronics
Tool,15.00,Hardware`;
    
    const testFilePath2 = path.join(__dirname, 'test-products.csv');
    fs.writeFileSync(testFilePath2, testData2);
    
    try {
      // Upload first file
      await page.getByRole('tab', { name: 'Upload' }).click();
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles([testFilePath, testFilePath2]);
      
      // Wait for both uploads to complete
      const completeElements = page.getByText('Complete');
      await expect(completeElements).toHaveCount(2, { timeout: 15000 });
      
      // Navigate to chat
      await page.getByRole('tab', { name: 'Chat' }).click();
      
      // Should show both files in context
      await expect(page.getByText('test-data.csv')).toBeVisible();
      await expect(page.getByText('test-products.csv')).toBeVisible();
      
      // Test querying with multiple files
      const chatInput = page.getByPlaceholder('Ask a question about your data...');
      await chatInput.fill('show me the first few rows of data');
      
      const sendButton = page.getByRole('button', { name: 'Send' });
      await sendButton.click();
      
      // Should get response without file not found errors
      await expect(page.getByText('AI is thinking...')).toBeVisible();
      const responseLocator = page.locator('[class*="bg-muted"]:has-text("Result")');
      await expect(responseLocator).toBeVisible({ timeout: 15000 });
      
      await expect(page.getByText('File \'file-')).not.toBeVisible();
      await expect(page.getByText('not found')).not.toBeVisible();
      
    } finally {
      // Clean up second test file
      if (fs.existsSync(testFilePath2)) {
        fs.unlinkSync(testFilePath2);
      }
    }
  });

  test('should handle network errors gracefully', async () => {
    // Test with invalid file to trigger error handling
    const invalidData = 'x'.repeat(600 * 1024 * 1024); // Larger than 500MB limit
    const invalidFilePath = path.join(__dirname, 'invalid-large-file.txt');
    fs.writeFileSync(invalidFilePath, invalidData);
    
    try {
      await page.getByRole('tab', { name: 'Upload' }).click();
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(invalidFilePath);
      
      // Should show error message
      await expect(page.getByText(/exceeds the 500MB limit/)).toBeVisible({ timeout: 10000 });
      
    } finally {
      // Clean up invalid file
      if (fs.existsSync(invalidFilePath)) {
        fs.unlinkSync(invalidFilePath);
      }
    }
  });
});

test.describe('Backend API Validation', () => {
  test('should verify backend file upload returns correct structure', async ({ request }) => {
    // Create test file
    const testData = 'name,value\ntest,123\n';
    const testBuffer = Buffer.from(testData);
    
    // Upload via API
    const response = await request.post('http://localhost:8000/api/v1/files/upload', {
      multipart: {
        file: {
          name: 'api-test.csv',
          mimeType: 'text/csv',
          buffer: testBuffer,
        },
      },
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    // Verify structure matches what frontend expects
    expect(data).toHaveProperty('file_id');
    expect(data).toHaveProperty('filename');
    expect(data).toHaveProperty('size');
    expect(data).toHaveProperty('message');
    expect(data.file_id).toMatch(/^file_\d+$/);
    
    // Clean up - delete the test file
    const deleteResponse = await request.delete(`http://localhost:8000/api/v1/files/${data.file_id}`);
    expect(deleteResponse.ok()).toBeTruthy();
  });

  test('should verify chat API works with correct file IDs', async ({ request }) => {
    // First upload a file
    const testData = 'name,value\ntest,123\nexample,456\n';
    const testBuffer = Buffer.from(testData);
    
    const uploadResponse = await request.post('http://localhost:8000/api/v1/files/upload', {
      multipart: {
        file: {
          name: 'chat-test.csv',
          mimeType: 'text/csv',
          buffer: testBuffer,
        },
      },
    });
    
    expect(uploadResponse.ok()).toBeTruthy();
    const uploadData = await uploadResponse.json();
    const fileId = uploadData.file_id;
    
    try {
      // Test chat with the file
      const chatResponse = await request.post('http://localhost:8000/api/v1/chat', {
        data: {
          message: 'describe the data',
          session_id: 'playwright-test',
          file_ids: [fileId]
        },
      });
      
      expect(chatResponse.ok()).toBeTruthy();
      const chatData = await chatResponse.json();
      
      // Should get valid response, not file not found error
      expect(chatData.response).not.toContain('File \'file-');
      expect(chatData.response).not.toContain('not found');
      expect(chatData.response).toContain('Result');
      
    } finally {
      // Clean up
      await request.delete(`http://localhost:8000/api/v1/files/${fileId}`);
    }
  });
});