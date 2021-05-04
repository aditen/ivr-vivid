import {LocatedObject} from "./LocatedObject";

export interface FilterCriteria {
    locatedObjects: LocatedObject[]
    classNames: string[]
    gridWidth: number
    text: string | null
}
