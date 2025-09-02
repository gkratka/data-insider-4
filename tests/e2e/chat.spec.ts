import { test, expect } from '@playwright/test'

test.describe('Chat Interface', () => {
  test('should display initial chat interface', async ({ page }) => {
    await page.goto('/')
    
    await expect(page.getByText('Hello! I\'m your data analysis assistant')).toBeVisible()
    await expect(page.getByPlaceholder('Ask me anything about your data')).toBeVisible()
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible()
  })

  test('should send a message and receive response', async ({ page }) => {
    await page.goto('/')
    
    const messageInput = page.getByPlaceholder('Ask me anything about your data')
    const sendButton = page.getByRole('button', { name: /send/i })
    
    // Type a message
    await messageInput.fill('Show me the summary statistics')
    await sendButton.click()
    
    // Should show user message in chat
    await expect(page.getByText('Show me the summary statistics')).toBeVisible()
    
    // Should clear the input
    await expect(messageInput).toHaveValue('')
    
    // Should show loading state
    await expect(page.getByText('Thinking...')).toBeVisible()
  })

  test('should display message history', async ({ page }) => {
    await page.goto('/')
    
    // Send multiple messages
    const messageInput = page.getByPlaceholder('Ask me anything about your data')
    const sendButton = page.getByRole('button', { name: /send/i })
    
    await messageInput.fill('First message')
    await sendButton.click()
    
    await page.waitForTimeout(1000) // Wait for first message to be processed
    
    await messageInput.fill('Second message')
    await sendButton.click()
    
    // Both messages should be visible
    await expect(page.getByText('First message')).toBeVisible()
    await expect(page.getByText('Second message')).toBeVisible()
  })

  test('should handle file context in chat', async ({ page }) => {
    await page.goto('/')
    
    // Assuming files are uploaded
    const messageInput = page.getByPlaceholder('Ask me anything about your data')
    
    await messageInput.fill('Tell me about the sales_data.csv file')
    await page.getByRole('button', { name: /send/i }).click()
    
    // Should show file context in response
    await expect(page.getByText(/sales_data.csv/)).toBeVisible()
  })

  test('should support voice input', async ({ page }) => {
    await page.goto('/')
    
    const voiceButton = page.getByRole('button', { name: /voice input/i })
    
    // Should have voice input button
    await expect(voiceButton).toBeVisible()
    
    // Click voice button should start recording
    await voiceButton.click()
    
    // Should show recording state
    await expect(page.getByText(/recording/i)).toBeVisible()
  })

  test('should clear chat history', async ({ page }) => {
    await page.goto('/')
    
    // Send a message first
    const messageInput = page.getByPlaceholder('Ask me anything about your data')
    await messageInput.fill('Test message')
    await page.getByRole('button', { name: /send/i }).click()
    
    // Clear chat
    const clearButton = page.getByRole('button', { name: /clear chat/i })
    await clearButton.click()
    
    // Confirm clear action
    await page.getByRole('button', { name: /confirm/i }).click()
    
    // Chat should be empty except for welcome message
    await expect(page.getByText('Test message')).not.toBeVisible()
    await expect(page.getByText('Hello! I\'m your data analysis assistant')).toBeVisible()
  })
})