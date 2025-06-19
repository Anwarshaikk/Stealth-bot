import React from 'react';
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  SortableContext,
  useSortable,
  arrayMove,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

export interface KanbanColumn {
  id: string;
  title: string;
}

export interface KanbanItem {
  id: string;
  status: string;
  candidate: string;
  job: string;
  updatedAt: string;
}

interface KanbanBoardProps {
  columns: KanbanColumn[];
  items: KanbanItem[];
  onDragEnd: (itemId: string, fromCol: string, toCol: string) => void;
}

const KanbanCard: React.FC<{
  item: KanbanItem;
  columnId: string;
}> = ({ item, columnId }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: item.id });

  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.7 : 1,
    zIndex: isDragging ? 50 : undefined,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      role="listitem"
      className="bg-surface-tier-0 rounded-lg p-3 shadow-sm hover:shadow-md cursor-grab select-none"
      tabIndex={0}
      aria-label={`Candidate ${item.candidate} for job ${item.job}`}
    >
      <div className="font-medium">{item.candidate}</div>
      <div className="text-sm text-text-secondary">{item.job}</div>
      <div className="text-xs text-text-secondary mt-1">{new Date(item.updatedAt).toLocaleString()}</div>
    </div>
  );
};

const KanbanBoard: React.FC<KanbanBoardProps> = ({ columns, items, onDragEnd }) => {
  // Group items by column id
  const itemsByCol: Record<string, KanbanItem[]> = React.useMemo(() => {
    const map: Record<string, KanbanItem[]> = {};
    columns.forEach(col => (map[col.id] = []));
    items.forEach(item => {
      if (map[item.status]) map[item.status].push(item);
    });
    return map;
  }, [columns, items]);

  // DnD sensors
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 10 } })
  );

  // Track active drag
  const [activeId, setActiveId] = React.useState<string | null>(null);
  const [draggedFromCol, setDraggedFromCol] = React.useState<string | null>(null);

  // Find which column an item is in
  const findColOfItem = (itemId: string): string | undefined => {
    for (const col of columns) {
      if (itemsByCol[col.id].some(i => i.id === itemId)) return col.id;
    }
    return undefined;
  };

  // Handle drag start
  const handleDragStart = (event: any) => {
    const { active } = event;
    setActiveId(active.id as string);
    setDraggedFromCol(findColOfItem(active.id as string) || null);
  };

  // Handle drag end
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);
    if (!over || !draggedFromCol) return;
    const itemId = active.id as string;
    const fromCol = draggedFromCol;
    const toCol = over.id as string;
    if (fromCol !== toCol) {
      onDragEnd(itemId, fromCol, toCol);
    }
    setDraggedFromCol(null);
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div
        className="flex space-x-4 overflow-x-auto p-4 lg:overflow-x-visible lg:grid lg:grid-cols-4 lg:space-x-0"
        role="list"
        aria-label="Kanban Columns"
      >
        {columns.map((col) => (
          <section
            key={col.id}
            aria-label={col.title}
            className="bg-surface-tier-1 rounded-lg p-4 w-64 flex-shrink-0 lg:w-auto lg:min-w-0 lg:max-w-full lg:overflow-visible lg:col-span-1"
          >
            <h3 className="text-lg font-semibold mb-4 text-text-primary flex items-center gap-2">
              {col.title}
              <span className="inline-block bg-primary text-white text-xs px-2 py-0.5 rounded-full font-bold">
                {itemsByCol[col.id].length}
              </span>
            </h3>
            <SortableContext
              items={itemsByCol[col.id].map(i => i.id)}
              strategy={verticalListSortingStrategy}
              id={col.id}
            >
              <div
                className="min-h-[200px] space-y-2"
                role="list"
                aria-label={`${col.title} items`}
                // Allow drop on column
                id={col.id}
              >
                {itemsByCol[col.id].map(item => (
                  <KanbanCard key={item.id} item={item} columnId={col.id} />
                ))}
              </div>
            </SortableContext>
          </section>
        ))}
      </div>
    </DndContext>
  );
};

export default KanbanBoard; 