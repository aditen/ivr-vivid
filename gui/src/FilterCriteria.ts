import {LocatedObject} from "./LocatedObject";
import {MinQuantity} from "./MinQuantity";

export interface FilterCriteria {
    locatedObjects: LocatedObject[],
    minQuantities: MinQuantity[],
    classNames: string[]
    gridWidth: number
    text: string | null
}
