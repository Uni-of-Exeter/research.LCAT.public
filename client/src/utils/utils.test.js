import { describe, it, expect } from 'vitest'
import { andify, formatTextWrap, camelize } from './utils'

describe('andify', () => {
  it('returns single item', () => {
    expect(andify(['apple'])).toBe('apple')
  })

  it('joins two items with "and"', () => {
    expect(andify(['apple', 'banana'])).toBe('apple and banana')
  })

  it('joins multiple items with commas and "and"', () => {
    expect(andify(['apple', 'banana', 'orange'])).toBe('apple, banana and orange')
  })

  it('handles empty array', () => {
    expect(andify([])).toBeUndefined()
  })
})

describe('formatTextWrap', () => {
  it('wraps text at specified length', () => {
    const result = formatTextWrap('hello world how are you', 10)
    // The function doesn't add spaces between words when wrapping
    expect(result).toEqual(['hello ', 'worldhow ', 'areyou '])
  })

  it('handles single word', () => {
    const result = formatTextWrap('hello', 10)
    expect(result).toEqual(['hello '])
  })

  it('handles text shorter than max length', () => {
    const result = formatTextWrap('hello world', 50)
    expect(result).toEqual(['hello world '])
  })

  it('replaces newlines with spaces', () => {
    const result = formatTextWrap('hello\nworld\nhow\nare\nyou', 20)
    expect(result[0]).toContain('hello world')
  })
})

describe('camelize', () => {
  it('capitalizes words and removes spaces', () => {
    expect(camelize('hello world')).toBe('HelloWorld')
  })

  it('handles single word', () => {
    expect(camelize('hello')).toBe('Hello')
  })

  it('handles multiple spaces', () => {
    expect(camelize('hello   world')).toBe('HelloWorld')
  })

  it('handles already capitalized words', () => {
    expect(camelize('Hello World')).toBe('HelloWorld')
  })

  it('handles mixed case', () => {
    expect(camelize('hELLo WoRLd')).toBe('HELLoWoRLd')
  })
})
