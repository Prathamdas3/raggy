import { Outlet, createRootRoute } from '@tanstack/react-router'
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools'
import { FormDevtoolsPanel } from "@tanstack/react-form-devtools"
import { HotkeysDevtoolsPanel } from "@tanstack/react-hotkeys-devtools"
import { TanStackDevtools } from '@tanstack/react-devtools'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

import '../styles.css'
import type { QueryClient } from '@tanstack/react-query'

interface MyRouterContext {
  queryClient: QueryClient;
}


export const Route = createRootRoute<MyRouterContext>({
  component: RootComponent,
})

function RootComponent() {
  return (
    <>
      <Outlet />
      <TanStackDevtools
        config={{
          position: 'bottom-right',
        }}
        plugins={[
          {
            name: 'TanStack Router',
            render: <TanStackRouterDevtoolsPanel />,
          },
          { name: "Tanstak Hotkeys", render: <HotkeysDevtoolsPanel /> },
          { name: "Tanstack Forms", render: <FormDevtoolsPanel /> },
          { name: "Tanstack Query", render: <ReactQueryDevtools /> }
        ]}
      />
    </>
  )
}
