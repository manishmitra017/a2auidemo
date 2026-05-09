import { basicCatalog } from '@a2ui/react/v0_9'
// @ts-expect-error BASIC_FUNCTIONS not in type declarations
import { BASIC_FUNCTIONS } from '@a2ui/web_core/v0_9/basic_catalog'

for (const fn of BASIC_FUNCTIONS) {
  (basicCatalog.functions as Record<string, unknown>)[fn.name] = fn
}

export { basicCatalog }
