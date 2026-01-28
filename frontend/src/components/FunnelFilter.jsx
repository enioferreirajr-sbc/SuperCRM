import { useState } from 'react';
import { FormControl, InputLabel, Select, MenuItem, OutlinedInput, Box, Chip, Checkbox, ListItemText } from '@mui/material';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
    PaperProps: {
        style: {
            maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
            width: 250,
        },
    },
};

export default function FunnelFilter({ options, selected, onChange }) {

    const handleChange = (event) => {
        const {
            target: { value },
        } = event;
        onChange(
            // On autofill we get a stringified value.
            typeof value === 'string' ? value.split(',') : value,
        );
    };

    return (
        <FormControl sx={{ m: 1, width: 300 }} size="small">
            <InputLabel id="funnel-filter-label">Funnel Percentage</InputLabel>
            <Select
                labelId="funnel-filter-label"
                id="funnel-filter"
                multiple
                value={selected}
                onChange={handleChange}
                input={<OutlinedInput label="Funnel Percentage" />}
                renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => (
                            <Chip key={value} label={value} size="small" />
                        ))}
                    </Box>
                )}
                MenuProps={MenuProps}
            >
                {options.map((option) => (
                    <MenuItem key={option} value={option}>
                        <Checkbox checked={selected.indexOf(option) > -1} />
                        <ListItemText primary={option} />
                    </MenuItem>
                ))}
            </Select>
        </FormControl>
    );
}
