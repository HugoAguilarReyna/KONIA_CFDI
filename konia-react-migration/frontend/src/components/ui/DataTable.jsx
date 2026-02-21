import React, { useRef, useMemo } from 'react';
import {
    useReactTable,
    getCoreRowModel,
    getSortedRowModel,
    flexRender,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react';
import clsx from 'clsx';

const DataTable = ({ data = [], columns, isLoading, height = 500 }) => {

    // Skeleton Loader
    if (isLoading) {
        return (
            <div className="glass-card w-full h-full overflow-hidden p-4">
                <div className="h-10 bg-slate-100 rounded mb-4 animate-pulse"></div>
                <div className="space-y-2">
                    {[...Array(10)].map((_, i) => (
                        <div key={i} className="h-12 bg-slate-50 rounded animate-pulse" style={{ opacity: 1 - i * 0.1 }}></div>
                    ))}
                </div>
            </div>
        );
    }

    // Table Instance
    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
    });

    // Virtualization
    const tableContainerRef = useRef(null);
    const { rows } = table.getRowModel();

    const rowVirtualizer = useVirtualizer({
        count: rows.length,
        getScrollElement: () => tableContainerRef.current,
        estimateSize: () => 48, // approximate row height
        overscan: 10,
    });

    return (
        <div className="glass-card w-full flex flex-col overflow-hidden bg-white rounded-xl shadow-sm border border-slate-100">
            {/* Header */}
            <div className="flex-none border-b border-slate-200 bg-slate-50/50 backdrop-blur-sm z-10">
                {table.getHeaderGroups().map(headerGroup => (
                    <div key={headerGroup.id} className="flex px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                        {headerGroup.headers.map(header => (
                            <div
                                key={header.id}
                                className={clsx(
                                    "flex items-center gap-1 cursor-pointer hover:text-slate-700 select-none",
                                    header.column.getCanSort() ? 'cursor-pointer' : ''
                                )}
                                style={{ width: header.getSize() }}
                                onClick={header.column.getToggleSortingHandler()}
                            >
                                {flexRender(header.column.columnDef.header, header.getContext())}
                                <span className="w-4">
                                    {{
                                        asc: <ArrowUp size={12} />,
                                        desc: <ArrowDown size={12} />,
                                    }[header.column.getIsSorted()] ?? (header.column.getCanSort() ? <ArrowUpDown size={12} className="opacity-0 hover:opacity-50" /> : null)}
                                </span>
                            </div>
                        ))}
                    </div>
                ))}
            </div>

            {/* Body */}
            <div
                ref={tableContainerRef}
                className="flex-1 overflow-auto custom-scrollbar"
                style={{ height }}
            >
                <div
                    style={{
                        height: `${rowVirtualizer.getTotalSize()}px`,
                        width: '100%',
                        position: 'relative',
                    }}
                >
                    {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                        const row = rows[virtualRow.index];
                        return (
                            <div
                                key={row.id}
                                className={clsx(
                                    "absolute top-0 left-0 w-full flex items-center px-4 border-b border-slate-50 hover:bg-slate-50/50 transition-colors",
                                    virtualRow.index % 2 === 0 ? 'bg-white' : 'bg-slate-50/20'
                                )}
                                style={{
                                    height: `${virtualRow.size}px`,
                                    transform: `translateY(${virtualRow.start}px)`,
                                }}
                            >
                                {row.getVisibleCells().map(cell => (
                                    <div
                                        key={cell.id}
                                        className="truncate text-sm text-slate-700"
                                        style={{ width: cell.column.getSize() }}
                                    >
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </div>
                                ))}
                            </div>
                        );
                    })}
                </div>

                {data.length === 0 && (
                    <div className="h-full flex items-center justify-center text-slate-400">
                        No hay datos para mostrar
                    </div>
                )}
            </div>
        </div>
    );
};

export default DataTable;
