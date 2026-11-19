import { createContext, useContext } from 'react'
import { tr, type Key, type Lang } from './i18n'
export type UiContext = { lang: Lang; role?: string; actions?: string[]; t: (key: Key) => string; toggleLang: () => void }
export const Context = createContext<UiContext>({ lang: 'en', role: 'organiser', actions: [], t: key => tr('en', key), toggleLang: () => {} })
export const useUi = () => useContext(Context)
