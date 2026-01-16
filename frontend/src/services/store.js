/**
 * Store global con Zustand para gestión de estado.
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Store de autenticación
export const useAuthStore = create(
  persist(
    (set) => ({
      isAuthenticated: false,
      token: null,

      login: (token) => {
        localStorage.setItem('osmoleads_token', token)
        set({ isAuthenticated: true, token })
      },

      logout: () => {
        localStorage.removeItem('osmoleads_token')
        set({ isAuthenticated: false, token: null })
      },

      checkAuth: () => {
        const token = localStorage.getItem('osmoleads_token')
        if (token) {
          set({ isAuthenticated: true, token })
          return true
        }
        return false
      },
    }),
    {
      name: 'osmoleads-auth',
      partialize: (state) => ({ isAuthenticated: state.isAuthenticated }),
    }
  )
)

// Store de países
export const useCountriesStore = create((set) => ({
  countries: [],
  selectedCountry: null,
  isLoading: false,

  setCountries: (countries) => set({ countries }),
  setSelectedCountry: (country) => set({ selectedCountry: country }),
  setLoading: (isLoading) => set({ isLoading }),

  addCountry: (country) =>
    set((state) => ({ countries: [...state.countries, country] })),

  updateCountry: (id, data) =>
    set((state) => ({
      countries: state.countries.map((c) =>
        c.id === id ? { ...c, ...data } : c
      ),
      selectedCountry:
        state.selectedCountry?.id === id
          ? { ...state.selectedCountry, ...data }
          : state.selectedCountry,
    })),

  removeCountry: (id) =>
    set((state) => ({
      countries: state.countries.filter((c) => c.id !== id),
      selectedCountry:
        state.selectedCountry?.id === id ? null : state.selectedCountry,
    })),
}))

// Store de leads
export const useLeadsStore = create((set) => ({
  leads: [],
  stats: {},
  currentTab: 'new',
  filters: {
    keyword_id: null,
    status_id: null,
    search: '',
  },
  isLoading: false,
  viewMode: 'cards', // 'cards' o 'list'

  setLeads: (leads) => set({ leads }),
  setStats: (stats) => set({ stats }),
  setCurrentTab: (tab) => set({ currentTab: tab }),
  setFilters: (filters) => set((state) => ({ filters: { ...state.filters, ...filters } })),
  clearFilters: () => set({ filters: { keyword_id: null, status_id: null, search: '' } }),
  setLoading: (isLoading) => set({ isLoading }),
  setViewMode: (mode) => set({ viewMode: mode }),

  updateLead: (id, data) =>
    set((state) => ({
      leads: state.leads.map((l) => (l.id === id ? { ...l, ...data } : l)),
    })),

  removeLead: (id) =>
    set((state) => ({
      leads: state.leads.filter((l) => l.id !== id),
    })),
}))

// Store de búsquedas
export const useSearchStore = create((set) => ({
  searchStats: {
    searches_today: 0,
    max_searches: 100,
    remaining: 100,
    is_unlimited: false,
  },
  isSearching: false,
  searchProgress: null,

  setSearchStats: (stats) => set({ searchStats: stats }),
  setSearching: (isSearching) => set({ isSearching }),
  setSearchProgress: (progress) => set({ searchProgress: progress }),
}))

// Store de configuración
export const useSettingsStore = create(
  persist(
    (set) => ({
      maxSearches: 100,
      statuses: [],
      marketplaces: [],

      setMaxSearches: (max) => set({ maxSearches: max }),
      setStatuses: (statuses) => set({ statuses }),
      setMarketplaces: (marketplaces) => set({ marketplaces }),

      addStatus: (status) =>
        set((state) => ({ statuses: [...state.statuses, status] })),

      updateStatus: (id, data) =>
        set((state) => ({
          statuses: state.statuses.map((s) =>
            s.id === id ? { ...s, ...data } : s
          ),
        })),

      removeStatus: (id) =>
        set((state) => ({
          statuses: state.statuses.filter((s) => s.id !== id),
        })),
    }),
    {
      name: 'osmoleads-settings',
    }
  )
)
