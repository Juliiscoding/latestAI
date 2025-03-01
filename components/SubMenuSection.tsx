import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "react-collapsible"
import { ChevronDown } from "lucide-react"
import Link from "next/link"

function SubMenuSection({ item }: { item: any }) {
  return (
    <Collapsible className="w-full">
      <CollapsibleTrigger className="flex w-full items-center gap-3 rounded-lg px-3 py-2 hover:bg-accent group">
        {item.icon && <item.icon className="h-4 w-4" />}
        <span className="flex-1 font-medium">{item.title}</span>
        {item.items && (
          <ChevronDown className="h-4 w-4 transition-transform duration-200 group-data-[state=open]:rotate-180" />
        )}
      </CollapsibleTrigger>
      {item.items && (
        <CollapsibleContent className="pl-9 py-2 space-y-2">
          {item.items.map((subItem: any) => (
            <Link
              key={subItem.title}
              href={subItem.url}
              className="flex w-full items-center rounded-lg px-3 py-1.5 text-sm hover:bg-accent"
            >
              {subItem.title}
            </Link>
          ))}
        </CollapsibleContent>
      )}
    </Collapsible>
  )
}

