import {LocatedObject} from "./LocatedObject";
import {Quantity} from "./Quantity";

export interface KeyframeFilterCriteria {
    locatedObjects: LocatedObject[],
    quantities: Quantity[],
    classNames: string[]
    text: string | null
}
