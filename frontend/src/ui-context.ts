import { createContext, useContext } from 'react'
import { tr, type Key, type Lang } from './i18n'
export type UiContext = { lang: Lang; t: (key: Key) => string }
export const Context = createContext<UiContext>({ lang: 'en', t: key => tr('en', key) })
export const useUi = () => useContext(Context)
