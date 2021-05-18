import {LocatedObject} from "./LocatedObject";
import {Quantity} from "./Quantity";

export interface FilterCriteria {
    locatedObjects: LocatedObject[],
    quantities: Quantity[],
    classNames: string[]
    gridWidth: number
    text: string | null
}
