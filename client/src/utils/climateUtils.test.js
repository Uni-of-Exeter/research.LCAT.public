import { describe, it, expect } from 'vitest'
import {
  climateChange,
  formatClimateData,
  climateVariables,
  getAllClimateData,
} from './climateUtils'

const buildPrediction = (overrides = {}) => [
  {
    tas_1980_mean: '10',
    tas_2050_mean: '12.5',
    pr_1980_mean: '1',
    pr_2050_mean: '2',
    rsds_1980_mean: '10',
    rsds_2050_mean: '12',
    sfcWind_1980_mean: '5',
    sfcWind_2050_mean: '3',
    ...overrides,
  },
]

describe('climateChange', () => {
  it('returns the difference between baseline and prediction', () => {
    const prediction = buildPrediction()
    expect(climateChange(prediction, 'tas', 2050)).toBe(2.5)
  })

  it('returns null when prediction is empty', () => {
    expect(climateChange([], 'tas', 2050)).toBeNull()
  })
})

describe('formatClimateData', () => {
  it('returns a no-data message when value is null', () => {
    const result = formatClimateData([], 'tas', 'Temperature', '°C', 2050)

    expect(result).toEqual({
      name: 'Temperature',
      value: null,
      change: 'No data yet for this area, coming soon.',
      arrow: null,
      direction: null,
    })
  })

  it('formats positive changes with an up arrow', () => {
    const prediction = buildPrediction({
      pr_1980_mean: '1',
      pr_2050_mean: '2',
    })
    const result = formatClimateData(prediction, 'pr', 'Rainfall', 'mm/day', 2050)

    expect(result).toMatchObject({
      name: 'Rainfall',
      value: 1,
      change: 'Rainfall increases by 1.00 mm/day',
      arrow: 'up',
      direction: 'increases',
      absoluteValue: '1.00',
      units: 'mm/day',
    })
  })

  it('formats negative changes with a down arrow', () => {
    const prediction = buildPrediction({
      sfcWind_1980_mean: '5',
      sfcWind_2050_mean: '3',
    })
    const result = formatClimateData(prediction, 'sfcWind', 'Windiness', 'm/sec', 2050)

    expect(result).toMatchObject({
      name: 'Windiness',
      value: -2,
      change: 'Windiness decreases by 2.00 m/sec',
      arrow: 'down',
      direction: 'decreases',
      absoluteValue: '2.00',
      units: 'm/sec',
    })
  })

  it('inverts rsds values to represent cloudiness', () => {
    const prediction = buildPrediction({
      rsds_1980_mean: '10',
      rsds_2050_mean: '12',
    })
    const result = formatClimateData(prediction, 'rsds', 'Cloudiness', 'Watts/m²', 2050)

    expect(result).toMatchObject({
      name: 'Cloudiness',
      value: -2,
      change: 'Cloudiness decreases by 2.00 Watts/m²',
      arrow: 'down',
      direction: 'decreases',
    })
  })

  it('formats zero change without arrows', () => {
    const prediction = buildPrediction({
      tas_1980_mean: '4',
      tas_2050_mean: '4',
    })
    const result = formatClimateData(prediction, 'tas', 'Temperature', '°C', 2050)

    expect(result).toMatchObject({
      name: 'Temperature',
      value: 0,
      change: 'No change in Temperature',
      arrow: 'none',
      direction: 'No change in',
    })
  })
})

describe('climateVariables', () => {
  it('defines the available climate variables', () => {
    expect(climateVariables).toEqual([
      { variable: 'tas', name: 'Temperature', units: '°C' },
      { variable: 'pr', name: 'Rainfall', units: 'mm/day' },
      { variable: 'rsds', name: 'Cloudiness', units: 'Watts/m²' },
      { variable: 'sfcWind', name: 'Windiness', units: 'm/sec' },
    ])
  })
})

describe('getAllClimateData', () => {
  it('formats climate data for each variable', () => {
    const prediction = [
      {
        tas_1980_mean: '10',
        tas_2100_mean: '11',
        pr_1980_mean: '3',
        pr_2100_mean: '5',
        rsds_1980_mean: '8',
        rsds_2100_mean: '7',
        sfcWind_1980_mean: '2',
        sfcWind_2100_mean: '4',
      },
    ]
    const result = getAllClimateData(prediction, 2100)

    expect(result).toHaveLength(4)
    expect(result[0]).toMatchObject({
      name: 'Temperature',
      value: 1,
      arrow: 'up',
    })
    expect(result[1]).toMatchObject({
      name: 'Rainfall',
      value: 2,
      arrow: 'up',
    })
    expect(result[2]).toMatchObject({
      name: 'Cloudiness',
      value: 1,
      arrow: 'up',
    })
    expect(result[3]).toMatchObject({
      name: 'Windiness',
      value: 2,
      arrow: 'up',
    })
  })
})
