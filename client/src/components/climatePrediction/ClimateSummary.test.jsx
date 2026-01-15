import React from 'react'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderToStaticMarkup } from 'react-dom/server'

vi.mock('./ClimateSummary.css', () => ({}))

vi.mock('react-loading-overlay-ts', () => ({
  default: ({ active, text, children }) => (
    <div data-active={String(active)} data-text={text}>
      {children}
    </div>
  ),
}))

vi.mock('../../images/buttons/decrease', () => ({
  default: () => <span data-icon="down">down</span>,
}))

vi.mock('../../images/buttons/increase', () => ({
  default: () => <span data-icon="up">up</span>,
}))

vi.mock('../../images/climate/CloudCover', () => ({
  default: () => <span>CloudIcon</span>,
}))

vi.mock('../../images/climate/Rain', () => ({
  default: () => <span>RainIcon</span>,
}))

vi.mock('../../images/climate/Temperature', () => ({
  default: () => <span>TempIcon</span>,
}))

vi.mock('../../images/climate/WindSpeed', () => ({
  default: () => <span>WindIcon</span>,
}))

vi.mock('../../utils/climateUtils', () => ({
  climateChange: vi.fn(),
  formatClimateData: vi.fn(),
}))

import ClimateSummary from './ClimateSummary'
import { climateChange, formatClimateData } from '../../utils/climateUtils'

const climateChangeMock = climateChange
const formatClimateDataMock = formatClimateData

const baseProps = {
  regions: [{ id: 1 }],
  loading: false,
  climatePrediction: [{ tas_1980_mean: '10', tas_2050_mean: '11' }],
  year: 2050,
}

describe('ClimateSummary', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns null when no regions are selected', () => {
    const markup = renderToStaticMarkup(
      <ClimateSummary
        regions={[]}
        loading={false}
        climatePrediction={baseProps.climatePrediction}
        year={baseProps.year}
      />,
    )

    expect(markup).toBe('')
    expect(climateChangeMock).not.toHaveBeenCalled()
  })

  it('renders summary text for each climate variable', () => {
    climateChangeMock.mockReturnValue(1)
    formatClimateDataMock.mockImplementation((_prediction, _variable, name) => ({
      change: `${name} summary`,
    }))

    const markup = renderToStaticMarkup(<ClimateSummary {...baseProps} />)

    expect(markup).toContain('Temperature summary')
    expect(markup).toContain('Rainfall summary')
    expect(markup).toContain('Cloudiness summary')
    expect(markup).toContain('Windiness summary')
    expect(climateChangeMock).toHaveBeenCalledWith(baseProps.climatePrediction, 'tas', 2050)
    expect(climateChangeMock).toHaveBeenCalledWith(baseProps.climatePrediction, 'pr', 2050)
    expect(climateChangeMock).toHaveBeenCalledWith(baseProps.climatePrediction, 'rsds', 2050)
    expect(climateChangeMock).toHaveBeenCalledWith(baseProps.climatePrediction, 'sfcWind', 2050)
  })

  it('renders arrows based on climate change direction (with rsds inversion)', () => {
    climateChangeMock.mockImplementation((_prediction, variable) => {
      if (variable === 'tas') return 1
      if (variable === 'pr') return -1
      if (variable === 'rsds') return 1
      if (variable === 'sfcWind') return 0
      return null
    })
    formatClimateDataMock.mockImplementation((_prediction, _variable, name) => ({
      change: `${name} summary`,
    }))

    const markup = renderToStaticMarkup(<ClimateSummary {...baseProps} />)
    const upCount = (markup.match(/data-icon="up"/g) || []).length
    const downCount = (markup.match(/data-icon="down"/g) || []).length

    expect(upCount).toBe(2)
    expect(downCount).toBe(2)
  })

  it('passes loading state to the overlay', () => {
    climateChangeMock.mockReturnValue(1)
    formatClimateDataMock.mockImplementation((_prediction, _variable, name) => ({
      change: `${name} summary`,
    }))

    const markup = renderToStaticMarkup(
      <ClimateSummary {...baseProps} loading={true} />,
    )

    expect(markup).toContain('data-active="true"')
    expect(markup).toContain('data-text="Loading climate data"')
  })
})
